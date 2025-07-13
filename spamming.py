import pandas as pd
import numpy as np
import re
import string
import nltk
import joblib
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import class_weight
from xgboost import XGBClassifier
from scipy.sparse import hstack

# === NLTK Setup ===
nltk.download('stopwords')
nltk.download('wordnet')

# === 1. Load Data ===
df = pd.read_csv('Phishing_Email.csv')
df = df.drop('Unnamed: 0', axis=1)  # Remove index column
df.columns = ['Email Text', 'Email Type']
df.dropna(subset=['Email Text', 'Email Type'], inplace=True)
df = df[df['Email Text'].str.len() > 10]
df['Email Text'] = df['Email Text'].astype(str).str.strip()
df['Email Type'] = df['Email Type'].astype(str).str.strip()

# === 2. Preprocessing ===
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    text = re.sub(r'\@w+|\#', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(w) for w in tokens if w not in stop_words]
    return ' '.join(tokens)

df['Cleaned_Text'] = df['Email Text'].apply(clean_text)

# === 3. Custom Features ===
def extract_features(text):
    text = text.lower()
    return [
        int(any(w in text for w in ['pdf', 'zip', 'doc', 'invoice', 'attachment'])),  # has_attachment
        int(any(w in text for w in ['urgent', 'immediately', 'reset', 'verify', 'click'])),  # has_urgency
        int(any(w in text for w in ['dear user', 'sir', 'madam', 'hello', 'supriya'])),  # has_salutation
        text.count("http"),  # number of links
        text.count("!"),  # exclamations
        sum(1 for w in text.split() if w.isupper() and len(w) > 1),  # ALL CAPS words
        len(text),  # total length
        len(text.split())  # word count
    ]

custom_features = np.array([extract_features(t) for t in df["Email Text"]])

# === 4. Encode Labels ===
label_encoder = LabelEncoder()
df['Label'] = label_encoder.fit_transform(df['Email Type'])  # Phishing = 0, Safe = 1

# === 5. TF-IDF ===
tfidf = TfidfVectorizer(ngram_range=(1, 3), stop_words='english', max_df=0.95, min_df=2, sublinear_tf=True)
X_tfidf = tfidf.fit_transform(df['Cleaned_Text'])

# === 6. Combine Features ===
X_combined = hstack([X_tfidf, custom_features])
y = df['Label']

# === 7. Split ===
X_train, X_test, y_train, y_test = train_test_split(X_combined, y, test_size=0.2, random_state=42)

# === 8. Compute Balanced Class Weights ===
sample_weights = class_weight.compute_sample_weight('balanced', y_train)

# === 9. Train Model ===
model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X_train, y_train, sample_weight=sample_weights)

# === 10. Save Model Assets ===
import os
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/model.pkl")
joblib.dump(tfidf, "model/vectorizer.pkl")
joblib.dump(label_encoder, "model/label_encoder.pkl")

# === 11. CLI Predictor ===
print("\n📨 Phishing Email Classifier v2 (XGBoost + TF-IDF + Custom Features)")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("📝 Email: ").strip()
    if user_input.lower() == 'exit':
        print("👋 Exiting. Stay alert!")
        break

    if len(user_input.split()) <= 5:
        print("🔍 Prediction: Safe Email (Phishing Confidence: 0.00%)\n")
        continue

    cleaned = clean_text(user_input)
    X_new_tfidf = tfidf.transform([cleaned])
    X_new_feat = np.array([extract_features(user_input)])
    X_new = hstack([X_new_tfidf, X_new_feat])

    probs = model.predict_proba(X_new)[0]
    phishing_index = list(label_encoder.classes_).index('Phishing Email')
    phishing_conf = probs[phishing_index] * 100

    if probs[phishing_index] > 0.6:
        pred_label = 'Phishing Email'
    else:
        pred_label = 'Safe Email'

    print(f"🔍 Prediction: {pred_label} (Phishing Confidence: {phishing_conf:.2f}%)\n")