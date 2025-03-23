from config.settings import ACTION_COLORS

def determine_action(results, threshold):
    """
    Determine moderation action based on toxicity results
    
    Args:
        results (dict): Toxicity results with scores
        threshold (float): Threshold for flagging content
        
    Returns:
        tuple: (action, color) - The recommended action and its display color
    """
    max_score = max(results.values())
    if max_score >= threshold + 0.2:
        return "FLAG", ACTION_COLORS["FLAG"]
    elif max_score >= threshold:
        return "REVIEW", ACTION_COLORS["REVIEW"]
    else:
        return "ALLOW", ACTION_COLORS["ALLOW"]