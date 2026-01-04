# gemini_api.py  — Flask bridge for VitaFuel
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# 1) Configure Gemini
genai.configure(api_key="YOUR_KEY_GOES_HERE")        # ← paste your key

model = genai.GenerativeModel("gemini-1.5-flash")   # or gemini-2.0-flash
chat  = model.start_chat()                          # single stateful chat

# 2) Spin up Flask
app = Flask(__name__)
CORS(app, origins="*")                              # allow browser fetch

@app.route("/gemini", methods=["POST"])
def gemini_reply():
    user_msg = request.json.get("message", "")
    if user_msg.lower() == "reset":                 # optional hard reset
        global chat
        chat = model.start_chat()
        return jsonify({"reply": "🔄 New conversation started!"})

    response = chat.send_message(user_msg)
    return jsonify({"reply": response.text})

if __name__ == "__main__":
    # visit http://localhost:5050/gemini (POST only)
    app.run(host="0.0.0.0", port=5050, debug=True)
