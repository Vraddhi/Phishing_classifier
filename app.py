from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import nltk
import imaplib
import email
from email.header import decode_header
import re
import string
import numpy as np
from email.utils import parsedate_to_datetime
from datetime import datetime
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from scipy.sparse import hstack

nltk.download('stopwords')
nltk.download('wordnet')

app = Flask(__name__)
CORS(app)

# Load model, vectorizer, and label encoder
model = joblib.load("model/model.pkl")
tfidf = joblib.load("model/vectorizer.pkl")
label_encoder = joblib.load("model/label_encoder.pkl")

# Setup NLTK
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Clean function (matching spamming.py)
def clean_text(text):
    if text is None:
        return ''
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    text = re.sub(r'\@w+|\#', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(w) for w in tokens if w not in stop_words]
    return ' '.join(tokens)

# Custom features function (matching spamming.py)
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

def decode_email_subject(subject):
    decoded_subject = decode_header(subject)
    subject_text = ""
    for content, charset in decoded_subject:
        if isinstance(content, bytes):
            try:
                subject_text += content.decode(charset or 'utf-8')
            except:
                subject_text += content.decode('utf-8', 'ignore')
        else:
            subject_text += content
    return subject_text

def get_email_body(message):
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                try:
                    return part.get_payload(decode=True).decode()
                except:
                    return part.get_payload(decode=True).decode('utf-8', 'ignore')
    else:
        try:
            return message.get_payload(decode=True).decode()
        except:
            return message.get_payload(decode=True).decode('utf-8', 'ignore')

@app.route('/fetch_emails', methods=['POST'])
def fetch_emails():
    # Email credentials
    email_address = "mainel5thsem@gmail.com"  # Your email
    password = "qrxw ussb lucl sodw"  # Your app password
    imap_server = "imap.gmail.com"
    
    try:
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, password)
        mail.select("inbox")
        
        # Search for all emails
        _, messages = mail.search(None, "ALL")
        email_list = []
        
        # Get all email numbers and fetch their dates
        email_nums = messages[0].split()
        email_dates = []
        
        # First pass: get all emails and their dates
        for num in email_nums:
            _, msg = mail.fetch(num, "(RFC822)")
            email_message = email.message_from_bytes(msg[0][1])
            date_str = email_message["date"]
            try:
                date = parsedate_to_datetime(date_str)
            except:
                date = datetime.now()  # fallback to current time if date parsing fails
            email_dates.append((num, date))
        
        # Sort by date in descending order (newest first)
        email_dates.sort(key=lambda x: x[1], reverse=True)
        
        # Get the last 10 emails
        for num, _ in email_dates[:10]:
            _, msg = mail.fetch(num, "(RFC822)")
            email_message = email.message_from_bytes(msg[0][1])
            
            # Extract email details
            subject = decode_email_subject(email_message["subject"])
            from_addr = email.utils.parseaddr(email_message["from"])[1]
            body = get_email_body(email_message)
            
            # Clean and analyze the email (matching spamming.py)
            cleaned = clean_text(body)
            X_new_tfidf = tfidf.transform([cleaned])
            X_new_feat = np.array([extract_features(body)])
            X_new = hstack([X_new_tfidf, X_new_feat])
            
            probs = model.predict_proba(X_new)[0]
            phishing_index = list(label_encoder.classes_).index('Phishing Email')
            phishing_conf = probs[phishing_index] * 100
            safe_conf = (1 - probs[phishing_index]) * 100
            
            pred_label = 'Phishing Email' if probs[phishing_index] > 0.6 else 'Safe Email'
            
            email_list.append({
                "from": from_addr,
                "subject": subject,
                "body": body,
                "prediction": pred_label,
                "phishing_probability": float(round(phishing_conf, 2)),
                "safe_probability": float(round(safe_conf, 2))
            })
        
        mail.close()
        mail.logout()
        
        return jsonify({
            "status": "success",
            "emails": email_list
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    email_text = data.get("email", "")
    
    if len(email_text.split()) <= 5:
        return jsonify({
            "prediction": "Safe Email",
            "phishing_probability": 0.0,
            "safe_probability": 100.0
        })
    
    cleaned = clean_text(email_text)
    X_new_tfidf = tfidf.transform([cleaned])
    X_new_feat = np.array([extract_features(email_text)])
    X_new = hstack([X_new_tfidf, X_new_feat])

    probs = model.predict_proba(X_new)[0]
    phishing_index = list(label_encoder.classes_).index('Phishing Email')
    phishing_conf = probs[phishing_index] * 100
    safe_conf = (1 - probs[phishing_index]) * 100

    pred_label = 'Phishing Email' if probs[phishing_index] > 0.6 else 'Safe Email'

    return jsonify({
        "prediction": pred_label,
        "phishing_probability": float(round(phishing_conf, 2)),
        "safe_probability": float(round(safe_conf, 2))
    })

if __name__ == "__main__":
    app.run(debug=True)
