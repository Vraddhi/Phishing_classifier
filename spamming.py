# Install necessary packages if not already installed
# pip install datasets pandas nltk scikit-learn

import pandas as pd
import nltk
from datasets import load_dataset
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report

# Download necessary NLTK data
nltk.download('stopwords')

# Load the phishing email dataset
ds = load_dataset("zefang-liu/phishing-email-dataset")

# Convert the dataset to a Pandas DataFrame
df = pd.DataFrame(ds['train'])

# Inspect the first few rows
print(df.head())

# Preprocess the 'Email Text' column
def clean_text(text):
    # Check if the text is None or empty
    if text is None:
        return ''
    
    # Lowercase text
    text = text.lower()
    
    # Remove stopwords using NLTK
    stopwords = nltk.corpus.stopwords.words('english')
    text = ' '.join([word for word in text.split() if word not in stopwords])
    
    return text


# Apply the clean_text function to the 'Email Text' column
df['cleaned_text'] = df['Email Text'].apply(clean_text)

# Display the cleaned data
print(df[['Email Text', 'cleaned_text']].head())

# Split the data into features and target
X = df['cleaned_text']
y = df['Email Type'].apply(lambda x: 1 if x == 'Phishing Email' else 0)  # 1 for phishing, 0 for safe

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Convert text to numerical features using CountVectorizer
vectorizer = CountVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train a Naive Bayes model
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test_vec)

# Evaluate the model's performance
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Test a new email
test_email = """
Subject: Meeting Reminder

Hi team,

Just a quick reminder that we have our weekly sync tomorrow at 10:00 AM in the main conference room. Please come prepared with updates on your current tasks and any blockers you're facing.

Let me know if you’re unable to attend.

Best,  
Ananya
"""

# Clean the test email using the same cleaning function
cleaned_test_email = clean_text(test_email)

# Use your vectorizer and model to predict
test_vector = vectorizer.transform([cleaned_test_email])
prediction = model.predict(test_vector)

print("\nTest Email Prediction:")
print("Phishing Email" if prediction[0] == 1 else "Safe Email")