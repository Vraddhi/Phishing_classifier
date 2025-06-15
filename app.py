from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import nltk
import imaplib
import email
from email.header import decode_header
import re
from email.utils import parsedate_to_datetime
from datetime import datetime
nltk.download('stopwords')

app = Flask(__name__)
CORS(app)

# Load model and vectorizer
with open("model/model.pkl", "rb") as f:
    model = pickle.load(f)

with open("model/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# Clean function
def clean_text(text):
    if text is None:
        return ''
    text = text.lower()
    stopwords = nltk.corpus.stopwords.words('english')
    return ' '.join([word for word in text.split() if word not in stopwords])

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
            
            # Clean and analyze the email
            cleaned = clean_text(body)
            vect = vectorizer.transform([cleaned])
            probas = model.predict_proba(vect)[0]
            
            email_list.append({
                "from": from_addr,
                "subject": subject,
                "body": body,
                "prediction": "Phishing Email" if probas[1] > 0.5 else "Safe Email",
                "phishing_probability": round(probas[1] * 100, 2),
                "safe_probability": round(probas[0] * 100, 2)
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
    cleaned = clean_text(email_text)
    vect = vectorizer.transform([cleaned])

    probas = model.predict_proba(vect)[0]  # [safe_prob, phishing_prob]
    phishing_prob = probas[1]
    safe_prob = probas[0]

    # Round to percentage
    phishing_percent = round(phishing_prob * 100, 2)
    safe_percent = round(safe_prob * 100, 2)

    label = "Phishing Email" if phishing_prob > 0.5 else "Safe Email"

    return jsonify({
        "prediction": label,
        "phishing_probability": phishing_percent,
        "safe_probability": safe_percent
    })

if __name__ == "__main__":
    app.run(debug=True)
