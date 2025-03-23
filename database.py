import firebase_admin
from firebase_admin import credentials, firestore
import datetime
from config.settings import FIREBASE_CONFIG_PATH

# Initialize Firebase
def initialize_firebase():
    """Initialize Firebase connection if not already initialized"""
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CONFIG_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()

def get_db():
    """Get Firestore client instance"""
    if not firebase_admin._apps:
        initialize_firebase()
    return firestore.client()

def save_analysis_to_firestore(username, content, results, action):
    """
    Save analysis results to Firestore
    
    Args:
        username (str): Username of content author
        content (str): Analyzed content
        results (dict): Toxicity analysis results
        action (str): Recommended action (FLAG, REVIEW, ALLOW)
    """
    db = get_db()
    analysis_data = {
        'username': username,
        'content': content,
        'results': results,
        'action': action,
        'timestamp': datetime.datetime.now()
    }
    db.collection('analyses').add(analysis_data)

def get_analyses():
    """
    Retrieve all analyses from Firestore
    
    Returns:
        list: List of analysis documents
    """
    db = get_db()
    return db.collection('analyses').stream()