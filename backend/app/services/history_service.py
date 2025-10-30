import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# History storage directory
HISTORY_DIR = Path("workspace/history")
HISTORY_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = HISTORY_DIR / "activity_history.json"


def load_history() -> List[Dict[str, Any]]:
    """Load history from file"""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def save_history(history: List[Dict[str, Any]]) -> None:
    """Save history to file"""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def add_history_entry(
    entry_type: str,
    description: str,
    details: str = None,
    user_id: str = "default"
) -> Dict[str, Any]:
    """
    Add a new history entry
    """
    history = load_history()
    
    entry = {
        'id': str(len(history) + 1),
        'timestamp': datetime.now().isoformat(),
        'type': entry_type,
        'description': description,
        'details': details,
        'user_id': user_id
    }
    
    history.insert(0, entry)
    
    # Keep only last 1000 entries
    history = history[:1000]
    
    save_history(history)
    
    return entry


def get_history(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get history entries
    """
    history = load_history()
    return history[:limit]


def clear_history() -> Dict[str, Any]:
    """
    Clear all history
    """
    save_history([])
    return {'success': True, 'message': 'History cleared'}


def get_statistics() -> Dict[str, Any]:
    """
    Get history statistics
    """
    history = load_history()
    
    stats = {
        'total_entries': len(history),
        'executions': len([h for h in history if h['type'] == 'execution']),
        'file_changes': len([h for h in history if h['type'] == 'file_change']),
        'workspace_changes': len([h for h in history if h['type'] == 'workspace_change'])
    }
    
    return stats
