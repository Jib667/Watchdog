"""
Database Initialization Script

This script initializes the database, creates all tables, and runs a first
synchronization with the Congress API if configured.
"""
import asyncio
import logging
import os
import sys
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from sync_manager import SyncManager
from config import is_api_configured, DATABASE_URL

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def initialize_database():
    """Initialize the database and run initial data synchronization."""
    try:
        logger.info(f"Using database at: {DATABASE_URL}")
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
        
        # Check if API is configured
        if not is_api_configured():
            logger.warning("Congress API key not configured. Skipping initial data sync.")
            logger.info("Set CONGRESS_API_KEY in your .env file to enable synchronization.")
            return
        
        # Create session and sync manager
        db = SessionLocal()
        try:
            sync_manager = SyncManager(db)
            
            # Run initial synchronization
            logger.info("Running initial data synchronization...")
            
            logger.info("Synchronizing representatives...")
            rep_result = await sync_manager.sync_representatives()
            logger.info(f"Representatives sync result: {rep_result['status']}")
            
            logger.info("Synchronizing recent bills...")
            bills_result = await sync_manager.sync_recent_bills(limit=100)
            logger.info(f"Bills sync result: {bills_result['status']}")
            
            logger.info("Synchronizing recent votes...")
            votes_result = await sync_manager.sync_recent_votes(limit=50)
            logger.info(f"Votes sync result: {votes_result['status']}")
            
            logger.info("Initial data synchronization completed.")
            
        except Exception as e:
            logger.error(f"Error during API synchronization: {e}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Starting database initialization...")
    asyncio.run(initialize_database())
    logger.info("Database initialization completed.") 