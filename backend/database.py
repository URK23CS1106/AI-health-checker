import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'history.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Create predictions table and add user_id foreign key
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symptoms_text TEXT,
            predictions_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def save_prediction(symptoms_text: str, predictions: list, user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO predictions (user_id, symptoms_text, predictions_json) VALUES (?, ?, ?)',
        (user_id, symptoms_text, json.dumps(predictions))
    )
    conn.commit()
    conn.close()

def get_history(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Filter history by user_id
    cursor.execute('SELECT * FROM predictions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "id": row["id"],
            "symptoms_text": row["symptoms_text"],
            "predictions": json.loads(row["predictions_json"]),
            "timestamp": row["timestamp"]
        })
    return history

def create_user(username: str, password_hash: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        user_id = None # Username already exists
    finally:
        conn.close()
    return user_id

def get_user(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None
