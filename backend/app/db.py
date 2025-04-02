"""
Consolidated Database Module for Watchdog Backend
"""

import os
import sqlite3
import logging
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration --- #
# Use BASE_DIR relative to this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'data')
DEFAULT_DB_PATH = os.path.join(DB_DIR, 'watchdog.db')

# Try getting from env, default, ensure it's just the path
raw_db_path = os.environ.get('DATABASE_URL', f"sqlite:///{DEFAULT_DB_PATH}")
if raw_db_path.startswith('sqlite:///'):
    DB_PATH = raw_db_path[len('sqlite:///'):]
else:
    DB_PATH = raw_db_path # Assume it's already a path if no prefix

# Ensure database directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# --- Database Connection --- #
def get_db_connection():
    """Get a database connection with row factory enabled"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error to {DB_PATH}: {e}")
        raise

# --- Pydantic Models --- #
# (Previously in models.py)

class UserBase(BaseModel):
    """Base user model."""
    username: str
    email: EmailStr # Use EmailStr for validation
    state: str
    district: Optional[str] = None
    # Removed full_name as it wasn't in the schema

class UserCreate(UserBase):
    """User creation model, includes password."""
    password: str

class UserInDBBase(UserBase):
    """Base model for User stored in DB."""
    id: int
    hashed_password: str
    representative_id: Optional[str] = None
    senator1_id: Optional[str] = None
    senator2_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True # Use orm_mode in Pydantic v1

class User(UserInDBBase):
    """User model returned by API."""
    pass # Inherits all fields

class UserInDB(UserInDBBase):
    """User model stored in DB (includes hashed password)."""
    pass # Inherits all fields

class Token(BaseModel):
    """Token model for authentication response."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Data payload within JWT token."""
    username: Optional[str] = None

# Removed Representative/Senator Pydantic models as data is static

# --- Database Initialization --- #
# (Previously in init_db.py)

def init_db():
    """Initialize the database with required tables."""
    logger.info(f"Initializing database schema at {DB_PATH}")
    conn = None # Ensure conn is defined in case of early error
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create users table (Updated Schema)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            state TEXT NOT NULL,
            district TEXT,           -- Nullable for states with one rep
            representative_id TEXT,    -- Link to static data ID
            senator1_id TEXT,          -- Link to static data ID
            senator2_id TEXT,          -- Link to static data ID
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Removed representatives and senators table creation

        conn.commit()
        logger.info("Database schema initialized successfully.")

    except sqlite3.Error as e:
        logger.error(f"Error initializing database schema: {e}")
        if conn: # Rollback if connection was established
            conn.rollback()
        raise # Re-raise the exception after logging
    finally:
        if conn:
            conn.close()

# --- Utility Functions (Optional - Keep if needed) --- #
# (Considered removing reset_db, backup_db, create_test_user)

def reset_db():
    """Reset the database: REMOVE existing file and re-initialize schema."""
    logger.warning(f"Attempting to reset database by deleting: {DB_PATH}")
    try:
        # Remove existing database if it exists
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            logger.info(f"Removed existing database file: {DB_PATH}")

        # Re-initialize schema (creates the file again)
        init_db()
        logger.info("Database reset and schema initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        return False

# Note: backup_db and create_test_user functions from original database.py
# have been removed for simplification. Add back if required.

# --- Main execution (for direct script running, e.g., reset) --- #
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        print(f"Resetting database: {DB_PATH}...")
        if reset_db():
            print("Database reset successful.")
        else:
            print("Database reset failed. Check logs.")
            sys.exit(1)
    else:
        print("Usage: python -m app.db reset")
        print("(Run from the 'backend' directory)")
        sys.exit(1) 