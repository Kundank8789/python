import json
from typing import Any, Dict
from datetime import datetime

def save_to_json(data: Dict[str, Any], filepath: str):
    """Save data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_from_json(filepath: str) -> Dict[str, Any]:
    """Load data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_timestamp() -> str:
    """Get current timestamp string"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text for display"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."