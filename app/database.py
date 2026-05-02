import sqlite3
import os

DB_NAME = "kocak_database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_NAME):
        conn = get_db_connection()
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT)')
        conn.execute('INSERT INTO users (username, role) VALUES ("admin", "administrator")')
        conn.commit()
        conn.close()

init_db()
