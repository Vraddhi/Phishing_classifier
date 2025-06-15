document.getElementById("fetchEmailBtn").addEventListener("click", () => {
    // Display a loading message
    document.getElementById('result').innerText = "Fetching and analyzing email...";
    document.getElementById('fromEmail').innerText = "";
    document.getElementById('subjectEmail').innerText = "";
    document.getElementById('bodyEmail').innerText = "";

    fetch("http://127.0.0.1:5000/fetch_emails", {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    })
    .then(res => res.json())
      .then(data => {
        if (data.status === "success" && data.emails.length > 0) {
            const lastEmail = data.emails[0]; // Get the last fetched email
            document.getElementById('fromEmail').innerText = lastEmail.from;
            document.getElementById('subjectEmail').innerText = lastEmail.subject;
            // Truncate body for display if too long
            document.getElementById('bodyEmail').innerText = lastEmail.body.substring(0, 200) + (lastEmail.body.length > 200 ? '...' : '');
            
            const resultText = `${lastEmail.prediction} (${lastEmail.phishing_probability}% phishing confidence)`;
            document.getElementById('result').innerText = resultText;
        } else if (data.status === "error") {
            document.getElementById("result").textContent = `Error: ${data.message}`;
        } else {
            document.getElementById("result").textContent = "No emails fetched or an unknown error occurred.";
        }
      })    
    .catch(err => {
      document.getElementById("result").textContent = "Error: Could not connect to Flask API";
      console.error(err);
    });
  });
  
      // .then(data => {
    //   document.getElementById("result").textContent = "Prediction: " + data.prediction;
    // })