#!/usr/bin/env python3
import os
import sys
import sqlite3
import logging
import hashlib
import shutil
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_PATH = os.environ.get('DATABASE_URL', 'sqlite:///./watchdog.db').replace('sqlite:///', '')

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initialize the database with tables for users and api configuration"""
    logger.info(f"Creating new database at {DATABASE_PATH}")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create tables - only user data and API config
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_config (
        id INTEGER PRIMARY KEY,
        api_key TEXT,
        base_url TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT,
        full_name TEXT,
        state TEXT,
        district TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS saved_representatives (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        congress_id TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE (user_id, congress_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS saved_bills (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        bill_id TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE (user_id, bill_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database tables created successfully")

def backup_database():
    """Create a backup of the existing database"""
    if os.path.exists(DATABASE_PATH):
        backup_path = f"{DATABASE_PATH}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Creating backup of existing database to {backup_path}")
        shutil.copy2(DATABASE_PATH, backup_path)
        return True
    return False

def create_test_user():
    """Create a test user"""
    logger.info("Creating test user")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name, state, district) VALUES (?, ?, ?, ?, ?, ?)",
            ("testuser", "test@example.com", hash_password("password123"), "Test User", "CA", "1")
        )
        conn.commit()
        logger.info("Created test user: username='testuser', password='password123'")
    except sqlite3.IntegrityError:
        logger.info("Test user already exists")
    
    conn.close()

def main():
    """Main function to reset the database"""
    logger.info("Starting database reset process")
    
    # Create a backup of the existing database
    backup_created = backup_database()
    if backup_created:
        logger.info("Backup created successfully")
    
    # Remove the existing database
    if os.path.exists(DATABASE_PATH):
        logger.info(f"Removing existing database at {DATABASE_PATH}")
        os.remove(DATABASE_PATH)
    
    # Create a new database with the correct schema
    init_db()
    
    # Create a test user
    create_test_user()
    
    logger.info("Database reset completed successfully")
    logger.info("You can now log in with the test user: username='testuser', password='password123'")

if __name__ == "__main__":
    main() 