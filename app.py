# from flask import Flask, request, jsonify
# import pickle
# import nltk
# nltk.download('stopwords')

# app = Flask(__name__)

# # Load model and vectorizer
# with open("model/model.pkl", "rb") as f:
#     model = pickle.load(f)

# with open("model/vectorizer.pkl", "rb") as f:
#     vectorizer = pickle.load(f)

# # Preprocess input
# def clean_text(text):
#     if text is None:
#         return ''
#     text = text.lower()
#     stopwords = nltk.corpus.stopwords.words('english')
#     return ' '.join([word for word in text.split() if word not in stopwords])

# @app.route('/predict', methods=['POST'])
# def predict():
#     data = request.get_json()
#     email_text = data.get("email", "")
#     cleaned = clean_text(email_text)
#     vect = vectorizer.transform([cleaned])
#     pred = model.predict(vect)[0]
#     label = "Phishing Email" if pred == 1 else "Safe Email"
#     return jsonify({"prediction": label})

# if __name__ == "__main__":
#     app.run(debug=True)





from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import nltk
nltk.download('stopwords')

app = Flask(__name__)
CORS(app)  # Enable CORS

# Load model and vectorizer
with open("model/model.pkl", "rb") as f:
    model = pickle.load(f)

with open("model/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

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
    pred = model.predict(vect)[0]
    label = "Phishing Email" if pred == 1 else "Safe Email"
    return jsonify({"prediction": label})

if __name__ == "__main__":
    app.run(debug=True)
