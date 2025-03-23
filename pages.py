import streamlit as st
from frontend.components import analytics_card, display_post
from services.analytics import get_analytics_data
from services.database import save_analysis_to_firestore
from services.moderation import determine_action
from models.toxicity import predict_toxicity
from config.settings import AVATAR_COLORS

def main_page(model, tokenizer):
    """
    Main page layout and functionality
    
    Args:
        model: The pre-trained model
        tokenizer: The tokenizer for the model
    """
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
                most_common = analytics_data['most_common_category'] or "none"
                category_count = analytics_data['category_counts'].get(most_common, 0) if most_common != "none" else 0
                
                st.markdown(f"""
                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">
                    Most common type:
                </div>
                <div style="font-weight: 600; margin-bottom: 0.75rem; font-size: 0.9rem;">{most_common.title()} ({category_count})</div>
                
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
            model,
            tokenizer,
            threshold,
            AVATAR_COLORS["sample1"]
        )
        
        display_post(
            "Alice Doe",
            "5 min ago",
            "The so-called \"experts\" are all just paid shills! Don't listen to their lies about climate change. They're trying to destroy our economy and way of life!",
            "AD",
            model,
            tokenizer,
            threshold,
            AVATAR_COLORS["sample2"]
        )
        
        # Analyze current input if button is clicked
        if analyze_button and content_input.strip():
            with st.spinner("Analyzing..."):
                results = predict_toxicity(model, tokenizer, content_input)
                action, _ = determine_action(results, threshold)
                save_analysis_to_firestore(display_name, content_input, results, action)
            
            # Display current input results with the username
            display_post(
                display_name,
                "Just now",
                content_input,
                user_initials,
                model,
                tokenizer,
                threshold,
                AVATAR_COLORS["user"]
            )
        elif analyze_button and not content_input.strip():
            st.warning("Please enter content to analyze")