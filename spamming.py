import pandas as pd
import nltk
from datasets import load_dataset
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
import os
import pickle

# Download stopwords if not present
nltk.download('stopwords')

# Load dataset
ds = load_dataset("zefang-liu/phishing-email-dataset")
df = pd.DataFrame(ds['train'])

# Clean text function
def clean_text(text):
    if text is None:
        return ''
    text = text.lower()
    stopwords = nltk.corpus.stopwords.words('english')
    return ' '.join([word for word in text.split() if word not in stopwords])

# Clean email text
df['cleaned_text'] = df['Email Text'].apply(clean_text)

# Prepare features and labels
X = df['cleaned_text']
y = df['Email Type'].apply(lambda x: 1 if x == 'Phishing Email' else 0)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Vectorize
vectorizer = CountVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train model
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# Evaluate
y_pred = model.predict(X_test_vec)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# 🧠 Save the model and vectorizer to disk
os.makedirs("model", exist_ok=True)

with open("model/model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("model/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print(" Model and vectorizer saved to /model/")
