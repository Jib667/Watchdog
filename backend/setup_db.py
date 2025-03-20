import os
import logging
import asyncio
from datetime import datetime

from database import engine, Base, ApiConfig, get_db
from congress_api import CongressAPI, sync_representatives, sync_recent_bills

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_database():
    """Set up the database and perform initial data synchronization."""
    # Create all tables if they don't exist
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    # Check if we have an API key
    api_key = os.getenv("CONGRESS_API_KEY")
    
    if not api_key:
        logger.warning(
            "No Congress API key found in environment variables. "
            "Please set CONGRESS_API_KEY environment variable or configure it via the API."
        )
        return
    
    # Check if API config already exists
    existing_config = db.query(ApiConfig).filter(ApiConfig.name == "congress_api").first()
    
    if existing_config:
        logger.info("Updating existing Congress API configuration...")
        existing_config.api_key = api_key
        existing_config.updated_at = datetime.utcnow()
    else:
        logger.info("Creating new Congress API configuration...")
        config = ApiConfig(
            name="congress_api",
            api_key=api_key,
            base_url=os.getenv("CONGRESS_API_URL", "https://api.congress.gov/v3"),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(config)
    
    db.commit()
    
    # Test API connection
    try:
        logger.info("Testing Congress API connection...")
        api = CongressAPI(db)
        response = await api._make_request("/congress", {"limit": 1})
        await api.close()
        logger.info("Successfully connected to Congress API")
        
        # If connection is successful, sync initial data
        logger.info("Starting initial data synchronization...")
        
        # Sync representatives
        await sync_representatives(db)
        
        # Sync recent bills (last 30 days)
        await sync_recent_bills(db, days_back=30)
        
        logger.info("Initial data synchronization complete")
        
    except Exception as e:
        logger.error(f"Error connecting to Congress API: {str(e)}")
        logger.error("Please check your API key and try again.")
    
    logger.info("Database setup complete")

if __name__ == "__main__":
    # Run the setup
    asyncio.run(setup_database()) 