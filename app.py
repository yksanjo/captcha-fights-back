"""
CAPTCHA That Fights Back - Flask Application
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from captcha_fights_back import ChallengeGenerator, BotScorer
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Store active challenges
challenges = {}
generator = ChallengeGenerator()
scorer = BotScorer()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>CAPTCHA That Fights Back</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .challenge { background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .answer-input { width: 100%; padding: 10px; margin: 10px 0; font-size: 16px; }
        .submit-btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .result { margin: 20px 0; padding: 15px; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>🧠 CAPTCHA That Fights Back</h1>
    <div id="challenge-container"></div>
    <div id="result-container"></div>
    
    <script>
        let challengeId = null;
        let interactions = [];
        let startTime = Date.now();
        
        // Track interactions
        document.addEventListener('mousemove', (e) => {
            interactions.push({
                x: e.clientX,
                y: e.clientY,
                timestamp: (Date.now() - startTime) / 1000,
                event_type: 'move'
            });
        });
        
        document.addEventListener('click', (e) => {
            interactions.push({
                x: e.clientX,
                y: e.clientY,
                timestamp: (Date.now() - startTime) / 1000,
                event_type: 'click'
            });
        });
        
        async function loadChallenge() {
            const response = await fetch('/api/v1/challenge/generate');
            const data = await response.json();
            challengeId = data.challenge_id;
            
            document.getElementById('challenge-container').innerHTML = `
                <div class="challenge">
                    <h3>${data.question}</h3>
                    <input type="text" id="answer" class="answer-input" placeholder="Your answer">
                    <button onclick="submitAnswer()" class="submit-btn">Submit</button>
                </div>
            `;
        }
        
        async function submitAnswer() {
            const answer = document.getElementById('answer').value;
            const browserFingerprint = {
                canvas_hash: 'normal',
                webgl_hash: 'normal'
            };
            
            const response = await fetch('/api/v1/challenge/verify', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    challenge_id: challengeId,
                    answer: answer,
                    interaction_path: interactions,
                    browser_fingerprint: browserFingerprint
                })
            });
            
            const result = await response.json();
            
            let resultHtml = '';
            if (result.verified) {
                resultHtml = `<div class="result success">✅ Verified! You're human.</div>`;
            } else {
                resultHtml = `<div class="result error">❌ ${result.message}</div>`;
            }
            
            document.getElementById('result-container').innerHTML = resultHtml;
            
            if (result.verified) {
                setTimeout(loadChallenge, 2000);
            }
        }
        
        loadChallenge();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    """Serve CAPTCHA interface."""
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/v1/challenge/generate", methods=["GET"])
def generate_challenge():
    """Generate a new challenge."""
    challenge = generator.generate_challenge()
    challenges[challenge["challenge_id"]] = {
        **challenge,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(minutes=5)
    }
    return jsonify(challenge)


@app.route("/api/v1/challenge/verify", methods=["POST"])
def verify_challenge():
    """Verify challenge answer."""
    data = request.json
    challenge_id = data.get("challenge_id")
    answer = data.get("answer", "").strip().lower()
    interaction_path = data.get("interaction_path", [])
    browser_fingerprint = data.get("browser_fingerprint", {})
    
    if challenge_id not in challenges:
        return jsonify({"verified": False, "message": "Invalid challenge ID"}), 400
    
    challenge = challenges[challenge_id]
    
    # Check expiration
    if datetime.now() > challenge["expires_at"]:
        del challenges[challenge_id]
        return jsonify({"verified": False, "message": "Challenge expired"}), 400
    
    # Check answer
    correct_answer = str(challenge["answer"]).strip().lower()
    answer_correct = answer == correct_answer
    
    # Score bot behavior
    bot_score_result = scorer.score(
        interaction_path=interaction_path,
        browser_fingerprint=browser_fingerprint,
        answer_correct=answer_correct
    )
    
    # Verify
    verified = answer_correct and not bot_score_result["is_bot"]
    
    # Clean up
    del challenges[challenge_id]
    
    if verified:
        return jsonify({
            "verified": True,
            "message": "Challenge passed",
            "bot_score": bot_score_result["bot_score"]
        })
    else:
        reason = []
        if not answer_correct:
            reason.append("Incorrect answer")
        if bot_score_result["is_bot"]:
            reason.append("Bot-like behavior detected")
        
        return jsonify({
            "verified": False,
            "message": "; ".join(reason) if reason else "Verification failed",
            "bot_score": bot_score_result["bot_score"]
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)




