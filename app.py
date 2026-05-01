import os
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- RATE LIMITER ---
limiter = Limiter(
    get_remote_address, 
    app=app, 
    default_limits=["300 per day"], 
    storage_uri="memory://"
)

# --- THE CLIENT SETUP ---
# Matching your curl's v1beta requirement
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={'api_version': 'v1beta'}
)

# --- SYSTEM BRAIN ---
SYSTEM_INFO = (
    "Identity: You are the professional AI Assistant for Axel Greg Parreño's Portfolio. "
    "MANDATORY: Always finish your sentences and complete the list you start. "
    "Privacy: Axel resigned from his night-shift role over a month ago to focus on his BSIT studies and health. "
    "Current Status: Fresh graduate at University of Cebu Main Campus, recently completed a Server & Network Admin internship. "
    "Recent Projects to Mention: "
    "- Sports Store Application: Built with ASP.NET Core MVC and C#, featuring a full product catalog and cart system. "
    "- TicTacToe: A simple implementation of the classic Tic-Tac-Toe game using ASP.NET CORE Razor Pages. Player vs AI is also implemented. "
    "- RESUMATE: An AI-powered resume analyzer tool. "
    "Response Style: Use bullet points for lists. Be professional, direct, and encouraging."
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
@limiter.limit("15 per minute") 
def ask_bot():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'reply': 'Please type something!'})

    try:
        # MODEL STRING MATCHED TO YOUR WORKING CURL: 'gemini-flash-latest'
        response = client.models.generate_content(
            model='gemini-flash-latest', 
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INFO,
                max_output_tokens=800, # Fixed the "incomplete sentence" issue
                temperature=0.4,
                top_p=0.95
            )
        )
        
        if not response.text:
            return jsonify({'reply': 'I am thinking... try that again!'})

        return jsonify({'reply': response.text.strip()})

    except Exception as e:
        error_msg = str(e)
        print(f"DEBUG ERROR: {error_msg}")
        
        # Catching the 503 Service Unavailable specifically
        if "503" in error_msg or "UNAVAILABLE" in error_msg:
            return jsonify({'reply': 'Google\'s AI servers are currently under high demand. Please wait a moment and try your question again!'})
        
        if "429" in error_msg:
            return jsonify({'reply': 'Rate limit hit. Please wait 60 seconds.'})
            
        return jsonify({'reply': 'I am having a bit of trouble connecting. Please refresh the page!'})

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)