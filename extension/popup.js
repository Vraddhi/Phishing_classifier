document.getElementById("checkBtn").addEventListener("click", () => {
    const email = document.getElementById("emailText").value;
  
    fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById("result").textContent = "Prediction: " + data.prediction;
    })
    .catch(err => {
      document.getElementById("result").textContent = "Error: Could not connect to Flask API";
      console.error(err);
    });
  });
  