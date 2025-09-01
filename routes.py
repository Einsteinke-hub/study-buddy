from flask import request, jsonify
from app import app
from models import Flashcard, StudySession
import requests
import json
from config import Config

# Hugging Face API integration for question generation
def generate_questions_with_hugging_face(text, num_questions=5):
    # This is a simplified example - you'll need to adjust based on the specific model you're using
    API_URL = "https://api-inference.huggingface.co/models/valhalla/t5-small-qa-qg-hl"
    headers = {"Authorization": f"Bearer {Config.HUGGING_FACE_API_KEY}"}
    
    # Prepare the payload based on the model's requirements
    payload = {
        "inputs": f"generate questions: {text}",
        "parameters": {
            "max_length": 200,
            "num_return_sequences": num_questions
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        
        # Process the result to extract questions and answers
        # This will vary based on the model's output format
        flashcards = []
        for i in range(num_questions):
            # This is a placeholder - you'll need to adjust based on the actual API response
            flashcards.append({
                "question": f"Sample question {i+1} from the text?",
                "answer": f"Sample answer {i+1} based on the text content."
            })
        
        return flashcards
    except Exception as e:
        print(f"Error calling Hugging Face API: {e}")
        return None

# Alternative: Simple rule-based question generation for demo purposes
def generate_questions_fallback(text, num_questions=5):
    # Simple implementation that creates questions from sentences
    sentences = text.split('. ')
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

@app.route('/api/generate-flashcards', methods=['POST'])
def generate_flashcards():
    data = request.get_json()
    text = data.get('text', '')
    topic = data.get('topic', 'general')
    num_questions = data.get('num_questions', 5)
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # Try to use Hugging Face API first
    flashcards = generate_questions_with_hugging_face(text, num_questions)
    
    # If API fails, use fallback method
    if not flashcards:
        flashcards = generate_questions_fallback(text, num_questions)
    
    # Save flashcards to database
    saved_ids = []
    for card in flashcards:
        flashcard_id = Flashcard.create(card['question'], card['answer'], topic)
        if flashcard_id:
            saved_ids.append(flashcard_id)
    
    # Record study session
    StudySession.create(topic, len(saved_ids))
    
    return jsonify({
        "message": f"Generated {len(saved_ids)} flashcards",
        "flashcards": flashcards,
        "saved_ids": saved_ids
    })

@app.route('/api/flashcards', methods=['GET'])
def get_flashcards():
    topic = request.args.get('topic')
    if topic:
        flashcards = Flashcard.get_by_topic(topic)
    else:
        flashcards = Flashcard.get_all()
    
    return jsonify({"flashcards": flashcards})

@app.route('/api/flashcards/<int:flashcard_id>', methods=['DELETE'])
def delete_flashcard(flashcard_id):
    success = Flashcard.delete(flashcard_id)
    if success:
        return jsonify({"message": "Flashcard deleted successfully"})
    else:
        return jsonify({"error": "Failed to delete flashcard"}), 500

@app.route('/api/study-sessions', methods=['GET'])
def get_study_sessions():
    sessions = StudySession.get_all()
    return jsonify({"sessions": sessions})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Study Buddy API is running"})