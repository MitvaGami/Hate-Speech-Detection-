import streamlit as st
from models.toxicity import predict_toxicity, keyword_filter_check
from services.moderation import determine_action
from config.settings import RISK_LEVELS, AVATAR_COLORS

def analytics_card(title, value, icon, color="#7986CB"):
    """
    Display an analytics card with a metric
    
    Args:
        title (str): Card title
        value (str): Value to display
        icon (str): Icon emoji
        color (str): Color for the value
    """
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

def display_post(author, time_ago, content, avatar_text, model, tokenizer, threshold=0.5, avatar_color=None):
    """
    Display a post with toxicity analysis
    
    Args:
        author (str): Post author name
        time_ago (str): Time indicator
        content (str): Post content
        avatar_text (str): Text to show in avatar
        model: The pre-trained model
        tokenizer: The tokenizer for the model
        threshold (float): Toxicity threshold
        avatar_color (str): Color for avatar background
    """
    if avatar_color is None:
        avatar_color = AVATAR_COLORS["default"]
        
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
    results = predict_toxicity(model, tokenizer, content)
    
    # Get top 2 categories for display
    top_categories = sorted(results.items(), key=lambda x: x[1], reverse=True)[:2]
    
    # Determine action
    action, action_color = determine_action(results, threshold)
    
    # Display results for top categories
    st.markdown('<div class="analysis-results">', unsafe_allow_html=True)
    
    for label, prob in top_categories:
        # Determine risk level
        if prob >= RISK_LEVELS["high"]["threshold"]:
            bar_class = RISK_LEVELS["high"]["class"]
        elif prob >= RISK_LEVELS["medium"]["threshold"]:
            bar_class = RISK_LEVELS["medium"]["class"]
        else:
            bar_class = RISK_LEVELS["low"]["class"]
            
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