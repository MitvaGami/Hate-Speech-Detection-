import streamlit as st

def load_css():
    """Load custom CSS styles for the application"""
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
                transition: all 0.2s ease-in-out !important;
            }
            
            .stButton button:hover {
                background-color: var(--primary-dark) !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
            }
            
            .stButton button:active {
                transform: translateY(0) !important;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
            }
        </style>
    """, unsafe_allow_html=True)