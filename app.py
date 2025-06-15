from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import nltk
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
