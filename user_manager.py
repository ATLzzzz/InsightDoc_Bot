# user_manager.py
import os
import json
from datetime import datetime
from filelock import FileLock
from config import USER_DATA_FILE

def load_user_data():
    """Memuat data pengguna dari file JSON."""
    if not os.path.exists(USER_DATA_FILE) or os.path.getsize(USER_DATA_FILE) == 0:
        return {}
    with open(USER_DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_user_data(data):
    """Menyimpan data pengguna ke file JSON."""
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def track_user(user, mode: str):
    """Melacak aktivitas pengguna dengan file locking."""
    lock = FileLock(f"{USER_DATA_FILE}.lock", timeout=10)
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