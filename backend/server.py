from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging
from datetime import datetime
import uvicorn
from config import PORT, DEBUG, is_api_configured, CONGRESS_API_KEY

# Import database models and session from the database module
from database import (
    User, Representative, Bill, Vote, ApiConfig,
    get_db, UserResponse, UserCreate, Session, ApiConfigResponse
)

# Import Congress API functions
from congress_api import (
    sync_representatives,
    sync_recent_bills,
    sync_member_votes,
    CongressAPI
)

# Import sync manager
from sync_manager import SyncManager, get_sync_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App initialization
app = FastAPI(
    title="Watchdog API", 
    description="API for monitoring Congress representatives and tracking their voting records"
)

# Configure CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
def read_root():
    """
    Root endpoint that returns a welcome message.
    Used to verify the API is running.
    """
    return {
        "message": "Welcome to the Watchdog API",
        "version": "1.0.0",
        "status": "operational"
    }

# ---------------------
# User Routes
# ---------------------

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user in the database.
    
    - Accepts user information including name, email, state, and subscription preference
    - Returns the created user with their assigned ID
    - Handles duplicates by returning a 400 error with details
    """
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    db_user = User(name=user.name, email=user.email, state=user.state, subscribed=user.subscribed)
    db.add(db_user)
    
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")
    
    return db_user

@app.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of users from the database.
    
    - Supports pagination with skip and limit parameters
    - Returns a list of user objects with all their details
    - Used for administrative interfaces to manage users
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific user by their ID.
    
    - Returns full user details for the specified user
    - Returns a 404 error if the user doesn't exist
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user from the database.
    
    - Removes the user with the specified ID
    - Returns a confirmation message if successful
    - Returns a 404 error if the user doesn't exist
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User with ID {user_id} deleted successfully"}

# ---------------------
# Representative Routes
# ---------------------

@app.get("/representatives/")
def get_representatives(
    chamber: Optional[str] = Query(None, description="Filter by chamber: 'House' or 'Senate'"),
    state: Optional[str] = Query(None, description="Filter by state (two-letter code)"),
    party: Optional[str] = Query(None, description="Filter by political party"),
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of representatives with optional filtering.
    
    - Can filter by chamber (House/Senate), state, or party
    - Supports pagination with skip and limit parameters
    - Returns a list of representative objects with their details
    """
    query = db.query(Representative)
    
    if chamber:
        query = query.filter(Representative.chamber == chamber)
    if state:
        query = query.filter(Representative.state == state)
    if party:
        query = query.filter(Representative.party == party)
    
    representatives = query.offset(skip).limit(limit).all()
    return representatives

@app.get("/representatives/{rep_id}")
def get_representative(rep_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific representative by their ID.
    
    - Returns full details for the specified representative
    - Returns a 404 error if the representative doesn't exist
    """
    rep = db.query(Representative).filter(Representative.id == rep_id).first()
    if rep is None:
        raise HTTPException(status_code=404, detail="Representative not found")
    return rep

# ---------------------
# Bill Routes
# ---------------------

@app.get("/bills/")
def get_bills(
    status: Optional[str] = Query(None, description="Filter by bill status"),
    session: Optional[int] = Query(None, description="Filter by Congress session"),
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of bills with optional filtering.
    
    - Can filter by status or Congress session
    - Supports pagination with skip and limit parameters
    - Returns a list of bill objects with their details
    """
    query = db.query(Bill)
    
    if status:
        query = query.filter(Bill.status == status)
    if session:
        query = query.filter(Bill.congress_session == session)
    
    bills = query.offset(skip).limit(limit).all()
    return bills

@app.get("/bills/{bill_id}")
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific bill by its ID.
    
    - Returns full details for the specified bill
    - Returns a 404 error if the bill doesn't exist
    """
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

# ---------------------
# Vote Routes
# ---------------------

@app.get("/votes/")
def get_votes(
    representative_id: Optional[int] = Query(None, description="Filter by representative ID"),
    bill_id: Optional[int] = Query(None, description="Filter by bill ID"),
    position: Optional[str] = Query(None, description="Filter by vote position"),
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of votes with optional filtering.
    
    - Can filter by representative, bill, or vote position
    - Supports pagination with skip and limit parameters
    - Returns a list of vote records with their details
    """
    query = db.query(Vote)
    
    if representative_id:
        query = query.filter(Vote.representative_id == representative_id)
    if bill_id:
        query = query.filter(Vote.bill_id == bill_id)
    if position:
        query = query.filter(Vote.vote_position == position)
    
    votes = query.offset(skip).limit(limit).all()
    return votes

@app.get("/representatives/{rep_id}/votes")
def get_representative_votes(
    rep_id: int, 
    position: Optional[str] = Query(None, description="Filter by vote position"),
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all votes cast by a specific representative.
    
    - Returns voting history for the specified representative
    - Can filter by vote position (Yes/No/Present/Not Voting)
    - Returns a 404 error if the representative doesn't exist
    """
    # Check if representative exists
    rep = db.query(Representative).filter(Representative.id == rep_id).first()
    if rep is None:
        raise HTTPException(status_code=404, detail="Representative not found")
    
    # Query votes
    query = db.query(Vote).filter(Vote.representative_id == rep_id)
    
    if position:
        query = query.filter(Vote.vote_position == position)
    
    votes = query.offset(skip).limit(limit).all()
    return votes

@app.get("/bills/{bill_id}/votes")
def get_bill_votes(
    bill_id: int, 
    position: Optional[str] = Query(None, description="Filter by vote position"),
    party: Optional[str] = Query(None, description="Filter by representative's party"),
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all votes cast on a specific bill.
    
    - Returns voting records for the specified bill
    - Can filter by vote position or representative's party
    - Returns a 404 error if the bill doesn't exist
    """
    # Check if bill exists
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    # Join Vote and Representative tables to filter by party if needed
    query = db.query(Vote).join(Representative).filter(Vote.bill_id == bill_id)
    
    if position:
        query = query.filter(Vote.vote_position == position)
    if party:
        query = query.filter(Representative.party == party)
    
    votes = query.offset(skip).limit(limit).all()
    return votes

# ---------------------
# Congress API Configuration Routes
# ---------------------

@app.get("/api/config", response_model=List[ApiConfigResponse])
def get_api_configs(db: Session = Depends(get_db)):
    """
    Retrieve all API configurations.
    
    - Returns all API configurations stored in the database
    - Used for administrative interfaces to manage API keys
    """
    configs = db.query(ApiConfig).all()
    return configs

@app.get("/api/config/{name}", response_model=ApiConfigResponse)
def get_api_config(name: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific API configuration by name.
    
    - Returns the configuration for the specified API
    - Returns a 404 error if the configuration doesn't exist
    """
    config = db.query(ApiConfig).filter(ApiConfig.name == name).first()
    if config is None:
        raise HTTPException(status_code=404, detail="API configuration not found")
    return config

@app.post("/api/config", response_model=ApiConfigResponse)
def create_or_update_api_config(config_data: ApiConfigResponse, db: Session = Depends(get_db)):
    """
    Create or update an API configuration.
    
    - If a configuration with the provided name already exists, it will be updated
    - Otherwise, a new configuration will be created
    - Returns the created or updated configuration
    """
    # Check if configuration already exists
    existing_config = db.query(ApiConfig).filter(ApiConfig.name == config_data.name).first()
    
    if existing_config:
        # Update existing configuration
        existing_config.api_key = config_data.api_key
        existing_config.base_url = config_data.base_url
        existing_config.is_active = config_data.is_active
        existing_config.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_config)
        return existing_config
    else:
        # Create new configuration
        new_config = ApiConfig(
            name=config_data.name,
            api_key=config_data.api_key,
            base_url=config_data.base_url,
            is_active=config_data.is_active,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        return new_config

# ---------------------
# Data Synchronization Routes
# ---------------------

@app.post("/api/sync/representatives")
def sync_representatives_endpoint(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Synchronize representatives data from the Congress API.
    
    - Fetches current representatives data from the Congress API
    - Updates existing records and creates new ones as needed
    - Runs as a background task to avoid blocking the API
    """
    # Add synchronization task to background
    background_tasks.add_task(sync_representatives, db)
    
    return {
        "status": "started",
        "message": "Representatives synchronization started in background"
    }

@app.post("/api/sync/bills")
def sync_bills_endpoint(
    background_tasks: BackgroundTasks, 
    days_back: int = Query(30, description="Number of days to look back for bills"),
    db: Session = Depends(get_db)
):
    """
    Synchronize recent bills data from the Congress API.
    
    - Fetches bills from the last specified number of days
    - Updates existing records and creates new ones as needed
    - Runs as a background task to avoid blocking the API
    """
    # Add synchronization task to background
    background_tasks.add_task(sync_recent_bills, db, days_back=days_back)
    
    return {
        "status": "started",
        "message": f"Bills synchronization started in background (looking back {days_back} days)"
    }

@app.post("/api/sync/representatives/{rep_id}/votes")
def sync_representative_votes_endpoint(
    rep_id: int = Path(..., description="Representative ID"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Synchronize voting records for a specific representative.
    
    - Fetches voting history for the specified representative
    - Updates existing records and creates new ones as needed
    - Can run in the background or immediately based on the request
    """
    # Verify representative exists
    rep = db.query(Representative).filter(Representative.id == rep_id).first()
    if rep is None:
        raise HTTPException(status_code=404, detail="Representative not found")
    
    if background_tasks:
        # Run in background
        background_tasks.add_task(sync_member_votes, db, rep_id)
        return {
            "status": "started",
            "message": f"Vote synchronization for representative {rep_id} started in background"
        }
    else:
        # Run immediately (for testing)
        import asyncio
        asyncio.run(sync_member_votes(db, rep_id))
        return {
            "status": "completed",
            "message": f"Vote synchronization for representative {rep_id} completed"
        }

@app.get("/api/test/congress-api")
async def test_congress_api(db: Session = Depends(get_db)):
    """
    Test the Congress API connection.
    
    - Attempts to connect to the Congress API using the stored configuration
    - Returns success or error message along with any data received
    - Used for verifying API keys and configuration
    """
    try:
        # Create API client
        api = CongressAPI(db)
        
        # Try to get the current Congress
        response = await api._make_request("/congress", {"limit": 1})
        
        # Close client
        await api.close()
        
        return {
            "status": "success",
            "message": "Successfully connected to Congress API",
            "data": response
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to connect to Congress API: {str(e)}"
        }

# Add dependency for sync manager
def get_sync_manager_dep(db: Session = Depends(get_db)):
    return get_sync_manager(db)

# Add routes for sync management
@app.get("/api/sync/status", response_model=Dict[str, Any])
async def get_sync_status(db: Session = Depends(get_db)):
    """Get the status of data synchronization with the Congress API."""
    try:
        # Check if API is configured
        api_configured = is_api_configured()
        
        # Get latest update timestamps
        latest_rep = db.query(Representative).order_by(
            Representative.last_updated.desc()
        ).first()
        
        latest_bill = db.query(Bill).order_by(
            Bill.last_updated.desc()
        ).first()
        
        latest_vote = db.query(Vote).order_by(
            Vote.last_updated.desc()
        ).first()
        
        return {
            "api_configured": api_configured,
            "latest_updates": {
                "representatives": latest_rep.last_updated.isoformat() if latest_rep else None,
                "bills": latest_bill.last_updated.isoformat() if latest_bill else None,
                "votes": latest_vote.last_updated.isoformat() if latest_vote else None
            },
            "record_counts": {
                "representatives": db.query(Representative).count(),
                "bills": db.query(Bill).count(),
                "votes": db.query(Vote).count()
            }
        }
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync/representatives", response_model=Dict[str, Any])
async def sync_representatives(
    force: bool = False,
    background_tasks: BackgroundTasks = None,
    sync_manager: SyncManager = Depends(get_sync_manager_dep)
):
    """Synchronize representatives data from the Congress API."""
    if not is_api_configured():
        raise HTTPException(status_code=400, detail="Congress API not configured")
    
    try:
        # If background tasks is provided, run in background
        if background_tasks:
            background_tasks.add_task(sync_manager.sync_representatives, force)
            return {"status": "started", "message": "Synchronization started in background"}
        
        # Otherwise run synchronously
        result = await sync_manager.sync_representatives(force)
        return result
    except Exception as e:
        logger.error(f"Error syncing representatives: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync/bills", response_model=Dict[str, Any])
async def sync_bills(
    limit: int = 100,
    force: bool = False,
    background_tasks: BackgroundTasks = None,
    sync_manager: SyncManager = Depends(get_sync_manager_dep)
):
    """Synchronize bills data from the Congress API."""
    if not is_api_configured():
        raise HTTPException(status_code=400, detail="Congress API not configured")
    
    try:
        # If background tasks is provided, run in background
        if background_tasks:
            background_tasks.add_task(sync_manager.sync_recent_bills, limit, force)
            return {"status": "started", "message": "Synchronization started in background"}
        
        # Otherwise run synchronously
        result = await sync_manager.sync_recent_bills(limit, force)
        return result
    except Exception as e:
        logger.error(f"Error syncing bills: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync/votes", response_model=Dict[str, Any])
async def sync_votes(
    limit: int = 50,
    force: bool = False,
    background_tasks: BackgroundTasks = None,
    sync_manager: SyncManager = Depends(get_sync_manager_dep)
):
    """Synchronize votes data from the Congress API."""
    if not is_api_configured():
        raise HTTPException(status_code=400, detail="Congress API not configured")
    
    try:
        # If background tasks is provided, run in background
        if background_tasks:
            background_tasks.add_task(sync_manager.sync_recent_votes, limit, force)
            return {"status": "started", "message": "Synchronization started in background"}
        
        # Otherwise run synchronously
        result = await sync_manager.sync_recent_votes(limit, force)
        return result
    except Exception as e:
        logger.error(f"Error syncing votes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync/all", response_model=Dict[str, Any])
async def sync_all(
    force: bool = False,
    background_tasks: BackgroundTasks = None,
    sync_manager: SyncManager = Depends(get_sync_manager_dep)
):
    """Synchronize all data from the Congress API."""
    if not is_api_configured():
        raise HTTPException(status_code=400, detail="Congress API not configured")
    
    try:
        # If background tasks is provided, run in background
        if background_tasks:
            background_tasks.add_task(sync_manager.run_full_sync, force)
            return {"status": "started", "message": "Full synchronization started in background"}
        
        # Otherwise run synchronously
        result = await sync_manager.run_full_sync(force)
        return result
    except Exception as e:
        logger.error(f"Error running full sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/api", response_model=Dict[str, Any])
async def get_api_config(db: Session = Depends(get_db)):
    """Get the API configuration status."""
    try:
        # Check if API key is configured
        api_key_configured = is_api_configured()
        
        # Get API configs from database
        api_configs = db.query(ApiConfig).all()
        
        return {
            "api_key_configured": api_key_configured,
            "api_configs": [
                {
                    "name": config.name,
                    "is_active": config.is_active,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat() if config.updated_at else None
                }
                for config in api_configs
            ]
        }
    except Exception as e:
        logger.error(f"Error getting API config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API Config model for updates
class ApiConfigUpdate(BaseModel):
    api_key: str
    base_url: Optional[str] = None
    is_active: Optional[bool] = True

@app.post("/api/config/api", response_model=Dict[str, Any])
async def update_api_config(
    config_data: ApiConfigUpdate,
    db: Session = Depends(get_db)
):
    """Update the API configuration."""
    try:
        # Check if config exists
        api_config = db.query(ApiConfig).filter_by(name="congress_api").first()
        
        if api_config:
            # Update existing config
            api_config.api_key = config_data.api_key
            if config_data.base_url:
                api_config.base_url = config_data.base_url
            api_config.is_active = config_data.is_active
            api_config.updated_at = datetime.utcnow()
        else:
            # Create new config
            api_config = ApiConfig(
                name="congress_api",
                api_key=config_data.api_key,
                base_url=config_data.base_url or "https://api.congress.gov/v3",
                is_active=config_data.is_active,
                created_at=datetime.utcnow()
            )
            db.add(api_config)
        
        db.commit()
        
        return {
            "status": "success",
            "message": "API configuration updated",
            "config": {
                "name": api_config.name,
                "is_active": api_config.is_active,
                "created_at": api_config.created_at.isoformat(),
                "updated_at": api_config.updated_at.isoformat() if api_config.updated_at else None
            }
        }
    except Exception as e:
        logger.error(f"Error updating API config: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Create tables
    from database import Base, engine
    Base.metadata.create_all(bind=engine)
    
    # Start server
    uvicorn.run("server:app", host="0.0.0.0", port=int(PORT), reload=DEBUG) 