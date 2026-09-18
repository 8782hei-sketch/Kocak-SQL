import sqlite3
import os
import json
from datetime import datetime

DB_DIR = "databases"
DEFAULT_DB = "kocak_database.db"

def get_db_path(db_name=None):
    """Get full path for database file"""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    if db_name is None:
        db_name = DEFAULT_DB
    return os.path.join(DB_DIR, db_name if db_name.endswith('.db') else f"{db_name}.db")

def get_db_connection(db_name=None):
    """Create database connection with foreign keys enabled"""
    db_path = get_db_path(db_name)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def list_databases():
    """List all available databases"""
    if not os.path.exists(DB_DIR):
        return []
    return [f for f in os.listdir(DB_DIR) if f.endswith('.db')]

def create_database(db_name):
    """Create a new database file"""
    db_path = get_db_path(db_name)
    if os.path.exists(db_path):
        return False, "Database already exists"
    conn = get_db_connection(db_name)
    conn.close()
    return True, "Database created successfully"

def delete_database(db_name):
    """Delete a database file"""
    if db_name == DEFAULT_DB:
        return False, "Cannot delete default database"
    db_path = get_db_path(db_name)
    if not os.path.exists(db_path):
        return False, "Database not found"
    os.remove(db_path)
    return True, "Database deleted successfully"

def init_default_db():
    """Initialize default database with sample schema"""
    db_path = get_db_path(DEFAULT_DB)
    if not os.path.exists(db_path):
        conn = get_db_connection(DEFAULT_DB)
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            table_name TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.execute("INSERT OR IGNORE INTO users (username, email, role) VALUES ('admin', 'admin@kocaksql.local', 'administrator')")
        conn.commit()
        conn.close()

init_default_db()
