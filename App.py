import streamlit as st
from frontend.styles import load_css
from frontend.pages import main_page
from services.database import initialize_firebase
from models.toxicity import load_model

# Initialize Firebase
initialize_firebase()

# Set page config FIRST
st.set_page_config(
    page_title="Toxicity Analyzer Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the model and tokenizer
model, tokenizer = load_model()

# Load custom CSS
load_css()

# Run main page
if __name__ == "__main__":
    main_page(model, tokenizer)