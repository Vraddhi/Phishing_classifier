##🛡️ Phishing Email Detection using NLP

This project detects phishing emails using Natural Language Processing (NLP) and machine learning models, integrated with a Flask backend, Chrome extension, and automatic Gmail inbox scanning via IMAP.



## 📌 Features

-  Detect if an email is **phishing or safe**
-  Display **phishing and safe probabilities (%)**
-  Auto-fetch last email from Gmail inbox
-  Chrome extension UI to classify emails with one click




## 🛠️ Setup Instructions

### 1.  Install Dependencies


pip install -r requirements.txt


##2.  Train the Model

python3 spamming.py
This trains a RandomForestClassifier with TfidfVectorizer and saves them to /model/.

##3.  Run Flask API

python3 app.py
By default, the Flask API runs at http://127.0.0.1:5000/.


## Chrome Extension Setup

Open chrome://extensions/
Enable Developer mode
Click Load unpacked
Select the /extension/ folder
Click the icon in Chrome to fetch and classify your latest email


🔒 Gmail Access Note
Enable 2FA and use an App Password for login

Your app.py connects via IMAP using:
email_address = "your-email@gmail.com"
password = "your-app-password"
