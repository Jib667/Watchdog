#!/usr/bin/env python3
"""
Database Initialization for Watchdog Backend

This script initializes the database schema for storing user information
and API configuration.
"""

import os
import sys
import logging
import sqlite3
import hashlib
import requests
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the database
DB_PATH = os.environ.get('DATABASE_URL', './backend/watchdog.db').replace('sqlite:///', '')

# Congress API configuration
API_KEY = os.environ.get("CONGRESS_API_KEY", "")
API_BASE_URL = os.environ.get("CONGRESS_API_URL", "https://api.congress.gov/v3")

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db_schema():
    """Initialize the database schema with required tables"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create tables
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
        logger.info("Database schema created successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database schema: {str(e)}")
        return False

def create_admin_user():
    """Create an admin user if it doesn't exist"""
    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD", "watchdog123")
    
    if not admin_username or not admin_password:
        logger.warning("Admin credentials not found in environment. Skipping admin user creation.")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if admin user already exists
        existing = cursor.execute("SELECT id FROM users WHERE username = ?", (admin_username,)).fetchone()
        
        if existing:
            logger.info(f"Admin user '{admin_username}' already exists.")
            conn.close()
            return True
        
        # Create admin user
        password_hash = hash_password(admin_password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)",
            (admin_username, "admin@watchdog.app", password_hash, "Watchdog Admin")
        )
        
        conn.commit()
        conn.close()
        logger.info(f"Created admin user: {admin_username}")
        return True
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        return False

def save_api_key():
    """Save the API key to the database if it exists"""
    if not API_KEY:
        logger.warning("No API key found in environment. Skipping API key configuration.")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Clear existing API config
        cursor.execute("DELETE FROM api_config")
        
        # Insert new API config
        cursor.execute(
            "INSERT INTO api_config (api_key, base_url) VALUES (?, ?)",
            (API_KEY, API_BASE_URL)
        )
        
        conn.commit()
        conn.close()
        logger.info("API key saved to database successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving API key to database: {str(e)}")
        return False

def test_api_connection():
    """Test the connection to the Congress.gov API"""
    if not API_KEY:
        logger.warning("No API key found. Skipping API connection test.")
        return False
    
    try:
        # Test a simple API endpoint
        url = f"{API_BASE_URL}/congress?api_key={API_KEY}&format=json"
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        if "congresses" in data:
            logger.info("API connection test successful")
            return True
        else:
            logger.warning("API response did not contain expected data")
            return False
    except Exception as e:
        logger.error(f"API connection test failed: {str(e)}")
        return False

def initialize_database():
    """Run the full database initialization process"""
    # Initialize the schema
    if not init_db_schema():
        logger.error("Failed to initialize database schema")
        return False
    
    # Create admin user
    create_admin_user()
    
    # Save API key
    save_api_key()
    
    # Test API connection
    test_api_connection()
    
    logger.info("Database initialization completed successfully")
    return True

if __name__ == "__main__":
    success = initialize_database()
    if success:
        print("Database initialization completed successfully.")
    else:
        print("Database initialization failed. Check the logs for details.")
        sys.exit(1) 