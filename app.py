from flask import Flask, request, jsonify, render_template
import openai
import sqlite3
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Database initialization
def init_db():
    conn = sqlite3.connect('interactions.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_input TEXT,
            bot_response TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Home route to render chat interface
@app.route('/')
def home():
    return render_template('chat.html')

# Chat API endpoint
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'response': "Please provide a message."}), 400

    response_text = get_ai_response(user_input)
    log_interaction(user_input, response_text)
    return jsonify({'response': response_text})

# Function to get AI response using OpenAI GPT
def get_ai_response(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful customer support assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Logging interaction into SQLite database
def log_interaction(user_input, response_text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('interactions.db')
    c = conn.cursor()
    c.execute("INSERT INTO interactions (timestamp, user_input, bot_response) VALUES (?, ?, ?)",
              (timestamp, user_input, response_text))
    conn.commit()
    conn.close()

# Route to get past interactions (optional)
@app.route('/logs')
def logs():
    conn = sqlite3.connect('interactions.db')
    c = conn.cursor()
    c.execute("SELECT timestamp, user_input, bot_response FROM interactions ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    app.run(debug=True)
