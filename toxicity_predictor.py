import streamlit as st
import pandas as pd
import numpy as np
from transformers import BertForSequenceClassification, BertTokenizer
import torch
import firebase_admin
from firebase_admin import credentials, firestore
import json
import datetime

# Initialize Firebase
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase_config.json')
        firebase_admin.initialize_app(cred)

initialize_firebase()
db = firestore.client()

# Set page config FIRST
st.set_page_config(
    page_title="Toxicity Analyzer Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the model and tokenizer
@st.cache_resource
def load_model():
    model_name = "unitary/toxic-bert"
    model = BertForSequenceClassification.from_pretrained(model_name)
    tokenizer = BertTokenizer.from_pretrained(model_name)
    return model, tokenizer

model, tokenizer = load_model()

# Function to predict toxicity
def predict_toxicity(sentence):
    inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True)
    
    with torch.no_grad():
        logits = model(**inputs).logits
    
    probs = torch.sigmoid(logits).squeeze().numpy()
    
    labels = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
    
    return {label: float(prob) for label, prob in zip(labels, probs)}

# Function to check if text would be caught by traditional keyword filtering
def keyword_filter_check(text):
    banned_words = ["idiot", "stupid", "hate", "kill", "damn", "hell","murder"]
    
    matches = [word for word in banned_words if word.lower() in text.lower()]
    
    if matches:
        return f"Keyword filter detection: {', '.join(matches)}"
    else:
        return "No keywords detected"

# Function to determine action based on toxicity scores
def determine_action(results, threshold):
    max_score = max(results.values())
    if max_score >= threshold + 0.2:
        return "FLAG", "#FF5252"  # Red
    elif max_score >= threshold:
        return "REVIEW", "#FFB74D"  # Amber
    else:
        return "ALLOW", "#4CAF50"  # Green

# Function to save analysis to Firestore
# Modify the save_analysis_to_firestore function to return the document ID
def save_analysis_to_firestore(username, content, results, action):
    analysis_data = {
        'username': username,
        'content': content,
        'results': {k: float(v) for k, v in results.items()},  # Ensure float conversion
        'action': action,
        'timestamp': datetime.datetime.now()
    }
    doc_ref = db.collection('analyses').add(analysis_data)
    return doc_ref[1].id  # Return the document ID

# New function to fetch recent analyses
def get_recent_analyses(limit=5):
    analyses_ref = db.collection('analyses')
    query = analyses_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
    
    recent_analyses = []
    for doc in query.stream():
        analysis = doc.to_dict()
        recent_analyses.append({
            'id': doc.id,
            'username': analysis.get('username', 'Anonymous'),
            'content': analysis.get('content', ''),
            'results': analysis.get('results', {}),
            'action': analysis.get('action', 'UNKNOWN'),
            'timestamp': analysis.get('timestamp')
        })
    
    return recent_analyses

# Function to get analytics data
def get_analytics_data():
    analyses = db.collection('analyses').stream()
    total_analyzed = 0
    total_flagged = 0
    total_passed = 0
    total_score = 0.0
    category_counts = {
        'toxic': 0,
        'severe_toxic': 0,
        'obscene': 0,
        'threat': 0,
        'insult': 0,
        'identity_hate': 0
    }
    
    for analysis in analyses:
        total_analyzed += 1
        results = analysis.to_dict()['results']
        action = analysis.to_dict()['action']
        
        if action in ['Block', 'Review']:
            total_flagged += 1
        else:
            total_passed += 1
        
        total_score += sum(results.values())
        
        for category, count in results.items():
            if count >= 0.5:
                category_counts[category] += 1
    
    avg_score = total_score / total_analyzed if total_analyzed > 0 else 0
    pass_rate = (total_passed / total_analyzed) * 100 if total_analyzed > 0 else 0
    
    most_common_category = max(category_counts, key=category_counts.get)
    
    return {
        'total_analyzed': total_analyzed,
        'total_flagged': total_flagged,
        'pass_rate': pass_rate,
        'avg_score': avg_score,
        'most_common_category': most_common_category,
        'category_counts': category_counts
    }

# Display sample post with analysis
def display_post(author, time_ago, content, avatar_text, avatar_color="#7986CB"):
    with st.container():
        st.markdown(
            f"""
            <div class="post-card">
                <div class="post-header">
                    <div class="avatar" style="background-color: {avatar_color};">
                        <span>{avatar_text}</span>
                    </div>
                    <div class="post-meta">
                        <div class="author">{author}</div>
                        <div class="time">{time_ago}</div>
                    </div>
                </div>
                <div class="post-content">
                    {content}
                </div>
            """,
            unsafe_allow_html=True
        )
    
    # Analyze the content
    results = predict_toxicity(content)
    
    # Get top 2 categories for display
    top_categories = sorted(results.items(), key=lambda x: x[1], reverse=True)[:2]
    
    # Determine action
    action, action_color = determine_action(results, 0.5)
    
    # Display results for top categories
    st.markdown('<div class="analysis-results">', unsafe_allow_html=True)
    
    for label, prob in top_categories:
        if prob >= 0.5:
            bar_color = "#FF5252"  # Red
            bar_class = "high-risk"
        elif prob >= 0.3:
            bar_color = "#FFB74D"  # Amber
            bar_class = "medium-risk"
        else:
            bar_color = "#4CAF50"  # Green
            bar_class = "low-risk"
            
        st.markdown(
            f"""
            <div class="metric-row">
                <div class="metric-label">{label.replace('_', ' ').title()}</div>
                <div class="metric-bar-container">
                    <div class="metric-bar {bar_class}" style="width: {prob * 100}%;"></div>
                </div>
                <div class="metric-value">{prob:.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Display action and comparison with keyword filtering
    keyword_result = keyword_filter_check(content)
    
    st.markdown(
        f"""
        <div class="action-row">
            <div class="action-tag" style="background-color: {action_color};">
                {action}
            </div>
            <div class="keyword-result">
                {keyword_result}
            </div>
        </div>
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Custom card component for analytics
def analytics_card(title, value, icon, color="#7986CB"):
    st.markdown(
        f"""
        <div class="analytics-card">
            <div class="analytics-icon" style="color: {color};">
                {icon}
            </div>
            <div class="analytics-content">
                <div class="analytics-title">{title}</div>
                <div class="analytics-value" style="color: {color};">{value}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Main app function
def main():
    # Dark theme CSS
    st.markdown("""
        <style>
            /* Global Styles */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            :root {
                --primary-color: #7986CB;
                --primary-light: #C5CAE9;
                --primary-dark: #3F51B5;
                --danger: #FF5252;
                --warning: #FFB74D;
                --success: #4CAF50;
                --text-primary: #E0E0E0;
                --text-secondary: #BDBDBD;
                --background: #121212;
                --card-bg: #1E1E1E;
                --card-header: #252525;
                --border: #333333;
                --input-bg: #2A2A2A;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background-color: var(--background);
                color: var(--text-primary);
                line-height: 1.5;
            }
            
            /* Override Streamlit's base styling */
            .stApp {
                background-color: var(--background);
            }
            
            /* Main container */
            .main {
                background-color: var(--background);
                padding: 0;
            }
            
            /* Header */
            .dashboard-header {
                background: linear-gradient(135deg, var(--primary-dark), #283593);
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1rem;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .header-title {
                color: white;
                font-size: 1.3rem;
                font-weight: 600;
                margin: 0;
            }
            
            .header-subtitle {
                color: rgba(255, 255, 255, 0.8);
                font-size: 0.85rem;
                font-weight: 400;
                margin-top: 0.2rem;
            }
            
            /* Section headings */
            .section-heading {
                font-size: 1rem;
                color: var(--text-primary);
                font-weight: 600;
                margin: 1rem 0 0.75rem 0;
                padding-bottom: 0.4rem;
                border-bottom: 2px solid var(--primary-dark);
                display: flex;
                align-items: center;
            }
            
            .section-heading::before {
                content: "";
                display: inline-block;
                width: 3px;
                height: 1rem;
                background-color: var(--primary-color);
                margin-right: 0.5rem;
                border-radius: 2px;
            }
            
            /* Analytics cards */
            .analytics-card-container {
                display: flex;
                gap: 0.75rem;
                margin-bottom: 1rem;
                flex-wrap: wrap;
            }
            
            .analytics-card {
                background-color: var(--card-bg);
                border-radius: 8px;
                padding: 0.75rem;
                display: flex;
                align-items: center;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                flex: 1;
                min-width: 160px;
                max-width: 200px;
                border: 1px solid var(--border);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .analytics-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
            }
            
            .analytics-icon {
                font-size: 1.2rem;
                margin-right: 0.75rem;
            }
            
            .analytics-content {
                flex: 1;
            }
            
            .analytics-title {
                font-size: 0.75rem;
                color: var(--text-secondary);
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .analytics-value {
                font-size: 1.4rem;
                font-weight: 600;
                margin-top: 0.2rem;
            }
            
            /* Posts */
            .post-card {
                background-color: var(--card-bg);
                border-radius: 8px;
                margin-bottom: 1rem; /* Reduced margin between posts */
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                border: 1px solid var(--border);
                max-width: 95%;
            }
            
            .post-header {
                display: flex;
                align-items: center;
                padding: 0.75rem;
                background-color: var(--card-header);
                border-bottom: 1px solid var(--border);
            }
            
            .avatar {
                width: 32px;
                height: 32px;
                border-radius: 6px;
                background-color: var(--primary-color);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                margin-right: 0.75rem;
                font-size: 0.8rem;
            }
            
            .post-meta {
                flex: 1;
            }
            
            .author {
                font-weight: 600;
                color: var(--text-primary);
                font-size: 0.85rem;
            }
            
            .time {
                color: var(--text-secondary);
                font-size: 0.75rem;
            }
            
            .post-content {
                padding: 0.75rem;
                font-size: 0.9rem;
                line-height: 1.4;
                color: black;
                border-bottom: 1px solid var(--border);
                background-color: #f0f0f0;
            }
            
            .analysis-results {
                padding: 0.75rem;
            }
            
            .metric-row {
                display: flex;
                align-items: center;
                margin-bottom: 0.4rem;
            }
            
            .metric-label {
                width: 100px;
                font-size: 0.8rem;
                font-weight: 500;
                color: var(--text-primary);
            }
            
            .metric-bar-container {
                flex: 1;
                height: 6px;
                background-color: #424242;
                border-radius: 3px;
                overflow: hidden;
                margin-right: 0.75rem;
            }
            
            .metric-bar {
                height: 100%;
                border-radius: 3px;
                transition: width 0.3s ease;
            }
            
            .high-risk {
                background-color: var(--danger);
            }
            
            .medium-risk {
                background-color: var(--warning);
            }
            
            .low-risk {
                background-color: var(--success);
            }
            
            .metric-value {
                width: 36px;
                font-size: 0.8rem;
                font-weight: 600;
                text-align: right;
                color: var(--text-secondary);
            }
            
            .action-row {
                display: flex;
                align-items: center;
                margin-top: 0.5rem;
                margin-bottom: 0.75rem; /* Added space after action row */
            }
            
            .action-tag {
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                color: white;
                font-size: 0.7rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-right: 0.75rem;
                margin-bottom: 0.5rem; /* Added space after action tag */
            }
            
            .keyword-result {
                color: var(--text-secondary);
                font-size: 0.75rem;
            }
            
            /* Input form */
            .input-container {
                background-color: var(--card-bg);
                border-radius: 8px;
                padding: 0.75rem;
                margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                border: 1px solid var(--border);
                max-width: 95%;
            }
            
            /* Sidebar */
            .css-1d391kg, .css-1cypcdb, .css-1offfwp {
                background-color: var(--background);
                border-right: 1px solid var(--border);
            }
            
            /* Sidebar text */
            .css-pkbazv, .css-17lntkn, .css-16idsys p, .sidebar-text, [data-testid="stSidebarNav"] {
                color: var(--text-primary) !important;
            }
            
            /* Text inputs in dark theme */
            .stTextInput div[data-baseweb="input"], .stTextArea textarea {
                background-color: var(--input-bg) !important;
                border: 1px solid var(--border) !important;
                border-radius: 6px !important;
                color: var(--text-primary) !important;
                box-shadow: none !important;
            }
            
            .stTextInput div[data-baseweb="input"]:focus-within, .stTextArea textarea:focus {
                border-color: var(--primary-color) !important;
                box-shadow: 0 0 0 1px var(--primary-color) !important;
            }
            
            /* Button */
            .stButton button {
                background-color: var(--primary-color) !important;
                color: white !important;
                font-weight: 500 !important;
                border-radius: 6px !important;
                padding: 0.3rem 1rem !important;
                border: none !important;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
                transition: all 0.2s !important;
                font-size: 0.85rem !important;
            }
            
            .stButton button:hover {
                background-color: var(--primary-dark) !important;
                box-shadow: 0 3px 6px rgba(0, 0, 0, 0.3) !important;
                transform: translateY(-1px) !important;
            }
            
            /* Slider in dark theme */
            .stSlider [data-baseweb=thumb] {
                background-color: var(--primary-color) !important;
                border-color: var(--primary-color) !important;
            }
            
            .stSlider [data-baseweb=track] {
                background-color: #424242 !important;
            }
            
            .stSlider [data-baseweb=tick] {
                background-color: #757575 !important;
            }
            
            /* Expander */
            .streamlit-expanderHeader {
                background-color: var(--card-header) !important;
                border-radius: 6px !important;
                color: var(--text-primary) !important;
                border: 1px solid var(--border) !important;
            }
            
            .streamlit-expanderContent {
                background-color: var(--card-bg) !important;
                border: 1px solid var(--border) !important;
                border-top: none !important;
                border-radius: 0 0 6px 6px !important;
            }

            /* Make labels visible in dark theme */
            label {
                color: var(--text-primary) !important;
            }

            /* Warning message */
            .stAlert {
                background-color: var(--card-bg) !important;
                color: var(--text-primary) !important;
                border: 1px solid var(--warning) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Compact Header
    st.markdown("""
        <div class="dashboard-header">
            <div>
                <h1 class="header-title">Toxicity Analyzer Pro</h1>
                <p class="header-subtitle">AI-powered content moderation</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Main layout with columns
    col1, col2 = st.columns([7, 3])
    
    with col2:
        # Settings Card
        with st.container():
            st.markdown('<div class="section-heading">Control Panel</div>', unsafe_allow_html=True)
            
            with st.expander("Toxicity Settings", expanded=True):
                threshold = st.slider(
                    "Detection Threshold",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.5,
                    step=0.01,
                    help="Adjust sensitivity for toxicity detection"
                )
                
                # Category toggles with more compact formatting
                st.markdown('<div style="margin: 0.5rem 0; font-weight: 500; font-size: 0.85rem;">Detection Categories</div>', unsafe_allow_html=True)
                
                categories = [
                    "Toxic",
                    "Severe Toxic", 
                    "Obscene",
                    "Threat",
                    "Insult",
                    "Identity Hate"
                ]
                
                # Category checkboxes in two columns for compact layout
                cat_cols = st.columns(2)
                selected_categories = {}
                
                for i, category in enumerate(categories):
                    with cat_cols[i % 2]:
                        selected_categories[category] = st.checkbox(category, value=True)
            
            # Analytics Dashboard Summary
            st.markdown('<div class="section-heading">Analytics</div>', unsafe_allow_html=True)
            
            # Get analytics data
            analytics_data = get_analytics_data()
            
            # Analysis metrics with icons in a more compact layout
            cols = st.columns(2)
            with cols[0]:
                analytics_card("Analyzed", f"{analytics_data['total_analyzed']}", "📊")
            with cols[1]:
                analytics_card("Flagged", f"{analytics_data['total_flagged']}", "⚠️", "#FF5252")
                
            cols = st.columns(2)
            with cols[0]:
                analytics_card("Pass Rate", f"{analytics_data['pass_rate']:.1f}%", "✅", "#4CAF50")
            with cols[1]:
                analytics_card("Avg Score", f"{analytics_data['avg_score']:.2f}", "📈", "#FFB74D")
            
            # Quick Stats
            with st.expander("Detailed Stats", expanded=False):
                st.markdown(f"""
                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">
                    Most common type:
                </div>
                <div style="font-weight: 600; margin-bottom: 0.75rem; font-size: 0.9rem;">{analytics_data['most_common_category'].title()} ({analytics_data['category_counts'][analytics_data['most_common_category']]})</div>
                
                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">
                    False positive rate:
                </div>
                <div style="font-weight: 600; font-size: 0.9rem;">8.2%</div>
                """, unsafe_allow_html=True)
                
    with col1:
        # Content Input Area
        st.markdown('<div class="section-heading">Content Analysis</div>', unsafe_allow_html=True)
        
        # User text input directly without the unnecessary container
        username = st.text_input("Author", placeholder="Enter name")
            
        # Display the current username or default
        display_name = username if username else "Anonymous User"
        user_initials = ''.join([name[0].upper() for name in display_name.split() if name])[:2]
        if not user_initials:
            user_initials = "AU"
        
        content_input = st.text_area(
            "Content",
            placeholder="Enter text to analyze for toxicity",
            height=80
        )
        
        button_cols = st.columns([4, 1])
        with button_cols[1]:
            analyze_button = st.button("Analyze", type="primary")
        
        # Results Section with added spacing between items
        st.markdown('<div class="section-heading">Recent Analysis</div>', unsafe_allow_html=True)
        
        # Sample posts with improved styling and increased spacing
        display_post(
            "John Smith",
            "2 min ago",
            "This movie is absolutely terrible! The director should be fired and the actors were completely useless.",
            "JS",
            "#7986CB"  # Indigo
        )
        
        display_post(
            "Alice Doe",
            "5 min ago",
            "The so-called \"experts\" are all just paid shills! Don't listen to their lies about climate change. They're trying to destroy our economy and way of life!",
            "AD",
            "#9575CD"  # Purple
        )
        
        # Analyze current input if button is clicked
        if analyze_button and content_input.strip():
            with st.spinner("Analyzing..."):
                results = predict_toxicity(content_input)
                action, _ = determine_action(results, threshold)
                save_analysis_to_firestore(display_name, content_input, results, action)
            
            # Display current input results with the username
            display_post(
                display_name,
                "Just now",
                content_input,
                user_initials,
                "#4DB6AC"  # Teal
            )
        elif analyze_button and not content_input.strip():
            st.warning("Please enter content to analyze")

# Run the app
if __name__ == "__main__":
    main()