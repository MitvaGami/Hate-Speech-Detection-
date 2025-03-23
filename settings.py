# Configuration settings
FIREBASE_CONFIG_PATH = 'firebase_config.json'

# Model settings
MODEL_NAME = "unitary/toxic-bert"

# Toxicity categories
TOXICITY_CATEGORIES = [
    'toxic', 
    'severe_toxic', 
    'obscene', 
    'threat', 
    'insult', 
    'identity_hate'
]

# Banned words for keyword filtering
BANNED_WORDS = ["idiot", "stupid", "hate", "kill", "damn", "hell"]

# Threshold settings
DEFAULT_THRESHOLD = 0.5

# UI Settings
AVATAR_COLORS = {
    "default": "#7986CB",
    "user": "#4DB6AC",
    "sample1": "#7986CB",
    "sample2": "#9575CD"
}

# Action colors
ACTION_COLORS = {
    "FLAG": "#FF5252",  # Red
    "REVIEW": "#FFB74D",  # Amber
    "ALLOW": "#4CAF50"   # Green
}

# Risk levels
RISK_LEVELS = {
    "high": {
        "threshold": 0.5,
        "color": "#FF5252",
        "class": "high-risk"
    },
    "medium": {
        "threshold": 0.3,
        "color": "#FFB74D",
        "class": "medium-risk"
    },
    "low": {
        "threshold": 0.0,
        "color": "#4CAF50",
        "class": "low-risk"
    }
}