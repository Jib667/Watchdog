#!/usr/bin/env python3
"""
Database Fix Utility for Watchdog Backend

This script provides utilities to fix or reset the database.
"""

import os
import sys
import logging
import sqlite3

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the database
DB_PATH = os.environ.get('DATABASE_URL', './backend/watchdog.db').replace('sqlite:///', '')

def reset_database():
    """Reset the database by removing it and recreating an empty one"""
    try:
        # Remove existing database if it exists
        if os.path.exists(DB_PATH):
            logger.info(f"Removing existing database at {DB_PATH}")
            os.remove(DB_PATH)
            logger.info("Database removed successfully")
        
        # Create the directory if it doesn't exist
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created directory {db_dir}")
        
        # Create an empty database file
        conn = sqlite3.connect(DB_PATH)
        conn.close()
        logger.info(f"Created new empty database at {DB_PATH}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to reset database: {str(e)}")
        return False

def show_usage():
    """Show script usage"""
    print("Watchdog Database Fix Utility")
    print("Usage:")
    print("  python fix_database.py [OPTIONS]")
    print("")
    print("Options:")
    print("  reset  - Reset the database (remove and recreate)")
    print("  help   - Show this help message")

if __name__ == "__main__":
    # Process command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "reset":
            success = reset_database()
            if success:
                print("Database reset completed successfully.")
            else:
                print("Database reset failed. Check the logs for details.")
                sys.exit(1)
        elif command == "help":
            show_usage()
        else:
            print(f"Unknown command: {command}")
            show_usage()
            sys.exit(1)
    else:
        # Default action: reset the database
        success = reset_database()
        if success:
            print("Database reset completed successfully.")
        else:
            print("Database reset failed. Check the logs for details.")
            sys.exit(1) 