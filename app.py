from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv
import stripe
from dotenv import load_dotenv
load_dotenv()

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'study_buddy'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Initialize database
def init_db():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create flashcards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flashcards (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                topic VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create study_sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                topic VARCHAR(255) NOT NULL,
                flashcards_count INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully")

# Initialize the database when the app starts
init_db()

# Simple question generation for demo
def generate_questions_fallback(text, num_questions=5):
    # Simple implementation that creates questions from sentences
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    flashcards = []
    
    for i, sentence in enumerate(sentences[:num_questions]):
        if sentence and len(sentence) > 10:  # Ensure the sentence is not too short
            # Create a simple question by replacing key terms
            question = sentence
            if ' is ' in sentence:
                question = sentence.replace(' is ', ' is what? ')
            elif ' are ' in sentence:
                question = sentence.replace(' are ', ' are what? ')
            else:
                question = f"What is {sentence.split(' ')[0]}?"
            
            flashcards.append({
                "question": question,
                "answer": sentence
            })
    
    return flashcards

# Root endpoint
@app.route('/')
def index():
    return jsonify({"message": "Study Buddy API is running", "endpoints": {
        "health": "/api/health",
        "generate_flashcards": "/api/generate-flashcards",
        "get_flashcards": "/api/flashcards",
        "get_study_sessions": "/api/study-sessions"
    }})

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Study Buddy API is running"})

# Generate flashcards endpoint
@app.route('/api/generate-flashcards', methods=['POST'])
def generate_flashcards():
    data = request.get_json()
    text = data.get('text', '')
    topic = data.get('topic', 'general')
    num_questions = data.get('num_questions', 5)
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # Use our fallback method for question generation
    flashcards = generate_questions_fallback(text, num_questions)
    
    # Save flashcards to database
    connection = get_db_connection()
    saved_ids = []
    if connection:
        cursor = connection.cursor()
        for card in flashcards:
            cursor.execute(
                "INSERT INTO flashcards (question, answer, topic) VALUES (%s, %s, %s)",
                (card['question'], card['answer'], topic)
            )
            saved_ids.append(cursor.lastrowid)
        
        # Record study session
        cursor.execute(
            "INSERT INTO study_sessions (topic, flashcards_count) VALUES (%s, %s)",
            (topic, len(saved_ids))
        )
        
        connection.commit()
        cursor.close()
        connection.close()
    
    return jsonify({
        "message": f"Generated {len(saved_ids)} flashcards",
        "flashcards": flashcards,
        "saved_ids": saved_ids
    })

# Get flashcards endpoint
@app.route('/api/flashcards', methods=['GET'])
def get_flashcards():
    topic = request.args.get('topic')
    connection = get_db_connection()
    flashcards = []
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        if topic:
            cursor.execute("SELECT * FROM flashcards WHERE topic = %s ORDER BY created_at DESC", (topic,))
        else:
            cursor.execute("SELECT * FROM flashcards ORDER BY created_at DESC")
        
        flashcards = cursor.fetchall()
        cursor.close()
        connection.close()
    
    return jsonify({"flashcards": flashcards})

# Delete flashcard endpoint
@app.route('/api/flashcards/<int:flashcard_id>', methods=['DELETE'])
def delete_flashcard(flashcard_id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM flashcards WHERE id = %s", (flashcard_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Flashcard deleted successfully"})
    else:
        return jsonify({"error": "Failed to delete flashcard"}), 500

# Get study sessions endpoint
@app.route('/api/study-sessions', methods=['GET'])
def get_study_sessions():
    connection = get_db_connection()
    sessions = []
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM study_sessions ORDER BY created_at DESC")
        sessions = cursor.fetchall()
        cursor.close()
        connection.close()
    
    return jsonify({"sessions": sessions})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)