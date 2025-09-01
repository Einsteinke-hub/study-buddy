from database import get_db_connection

class Flashcard:
    def __init__(self, id, question, answer, topic, created_at):
        self.id = id
        self.question = question
        self.answer = answer
        self.topic = topic
        self.created_at = created_at
    
    @staticmethod
    def create(question, answer, topic):
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO flashcards (question, answer, topic) VALUES (%s, %s, %s)",
                (question, answer, topic)
            )
            connection.commit()
            flashcard_id = cursor.lastrowid
            cursor.close()
            connection.close()
            return flashcard_id
        return None
    
    @staticmethod
    def get_all():
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM flashcards ORDER BY created_at DESC")
            flashcards = cursor.fetchall()
            cursor.close()
            connection.close()
            return flashcards
        return []
    
    @staticmethod
    def get_by_topic(topic):
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM flashcards WHERE topic = %s ORDER BY created_at DESC", (topic,))
            flashcards = cursor.fetchall()
            cursor.close()
            connection.close()
            return flashcards
        return []
    
    @staticmethod
    def delete(flashcard_id):
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM flashcards WHERE id = %s", (flashcard_id,))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        return False

class StudySession:
    def __init__(self, id, topic, flashcards_count, created_at):
        self.id = id
        self.topic = topic
        self.flashcards_count = flashcards_count
        self.created_at = created_at
    
    @staticmethod
    def create(topic, flashcards_count):
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO study_sessions (topic, flashcards_count) VALUES (%s, %s)",
                (topic, flashcards_count)
            )
            connection.commit()
            session_id = cursor.lastrowid
            cursor.close()
            connection.close()
            return session_id
        return None
    
    @staticmethod
    def get_all():
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM study_sessions ORDER BY created_at DESC")
            sessions = cursor.fetchall()
            cursor.close()
            connection.close()
            return sessions
        return []