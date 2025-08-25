# user_manager.py
import os
import json
from datetime import datetime
from filelock import FileLock # Use the cross-platform filelock library

from config import USER_DATA_FILE

def load_user_data():
    """Loads user data from the JSON file."""
    if not os.path.exists(USER_DATA_FILE):
        return {}
    # Ensure the file is not empty before trying to load JSON
    if os.path.getsize(USER_DATA_FILE) > 0:
        with open(USER_DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} # Return empty dict if file is corrupt
    return {}

def save_user_data(data):
    """Saves user data to the JSON file."""
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def track_user(user, mode: str):
    """Tracks a user's activity with file locking to prevent race conditions."""
    lock_path = f"{USER_DATA_FILE}.lock"
    lock = FileLock(lock_path, timeout=10)

    with lock:
        users = load_user_data()
        user_id = str(user.id)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if user_id in users:
            users[user_id]['usage_count'] += 1
            users[user_id]['last_used'] = now
            users[user_id]['last_mode'] = mode
        else:
            users[user_id] = {
                'first_name': user.first_name,
                'username': user.username or 'N/A',
                'usage_count': 1,
                'first_used': now,
                'last_used': now,
                'last_mode': mode
            }
        
        save_user_data(users)