import streamlit as st
import torch
from transformers import BertForSequenceClassification, BertTokenizer
from config.settings import MODEL_NAME, TOXICITY_CATEGORIES, BANNED_WORDS

@st.cache_resource
def load_model():
    """
    Load the BERT model and tokenizer for toxicity detection
    """
    model = BertForSequenceClassification.from_pretrained(MODEL_NAME)
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
    return model, tokenizer

def predict_toxicity(model, tokenizer, sentence):
    """
    Predict toxicity scores for a given sentence
    
    Args:
        model: The pre-trained model
        tokenizer: The tokenizer for the model
        sentence (str): Input text to analyze
        
    Returns:
        dict: Dictionary with toxicity scores for each category
    """
    inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True)
    
    with torch.no_grad():
        logits = model(**inputs).logits
    
    probs = torch.sigmoid(logits).squeeze().numpy()
    
    return {label: float(prob) for label, prob in zip(TOXICITY_CATEGORIES, probs)}

def keyword_filter_check(text):
    """
    Check if text contains banned keywords
    
    Args:
        text (str): Text to check
        
    Returns:
        str: Message indicating detected keywords or None
    """
    matches = [word for word in BANNED_WORDS if word.lower() in text.lower()]
    
    if matches:
        return f"Keyword filter detection: {', '.join(matches)}"
    else:
        return "No keywords detected"