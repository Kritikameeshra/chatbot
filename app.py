from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# Set environment variables
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Initialize Flask application
app = Flask(__name__)

# Configure session to use filesystem (server-side session management)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'your_secret_key_here'
Session(app)

@app.route('/')
def index():
    # Initialize chat history in session
    if 'history' not in session:
        session['history'] = []
        welcome_message = "MindCareBot: Hello! I’m here to support your mental well-being. How are you feeling today?"
        session['history'].append({'message': welcome_message, 'sender': 'bot'})
    return render_template('index.html', history=session['history'])

@app.route('/submit', methods=['POST'])
def on_submit():
    query = request.form['query']
    session.setdefault('history', []).append({'message': query, 'sender': 'user'})
    
    response = generate_response(query)
    response_message = f"MindCareBot Response: {response}"
    session['history'].append({'message': response_message, 'sender': 'bot'})
    
    return jsonify({'query': query, 'response': response_message})

def generate_response(query):
    # Directly generate a response to the user's query using Google Generative AI
    qa_prompt = "You are MindCareBot, a mental health assistant designed to offer emotional support, coping strategies, and guidance to users struggling with stress, anxiety, depression, or other mental health challenges. You aim to create a safe, non-judgmental, and supportive environment where users can express their emotions freely. Provide thoughtful, empathetic, and practical advice to users based on their queries. If a situation requires professional help, encourage them to seek it, but also offer comforting suggestions such as breathing exercises, mindfulness tips, and self-care practices. Keep your tone calm, compassionate, and encouraging. You should also suggest follow-up actions that users can take to improve their mental well-being."
    input_text = f"{qa_prompt}\nUser question:\n{query}"
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    result = llm.invoke(input_text)
    return result.content

if __name__ == '__main__':
    app.run(debug=True)
