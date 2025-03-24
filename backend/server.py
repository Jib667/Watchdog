from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
import os
import sqlite3
import requests
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import hashlib
import jwt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Watchdog API", description="Simple API for Congressional Watchdog Application")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],  # Allow your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_KEY = os.environ.get("CONGRESS_API_KEY", "")
API_BASE_URL = os.environ.get("CONGRESS_API_URL", "https://api.congress.gov/v3")
DATABASE_PATH = os.environ.get('DATABASE_URL', 'sqlite:///./watchdog.db').replace('sqlite:///', '')
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24  # 24 hours

# Create database directory if it doesn't exist
os.makedirs(os.path.dirname(DATABASE_PATH) if os.path.dirname(DATABASE_PATH) else '.', exist_ok=True)

# OAuth2 scheme for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# Pydantic models
class ApiConfig(BaseModel):
    api_key: str
    base_url: str = 'https://api.congress.gov/v3'

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    state: Optional[str] = None  # User's state (e.g., 'CA', 'NY')
    district: Optional[str] = None  # User's congressional district (e.g., '1', '2', 'At-Large')

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool = True

class UserInDB(User):
    password_hash: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class Representative(BaseModel):
    congress_id: str
    name: str
    state: str
    district: Optional[str] = None
    party: str
    chamber: str

class Bill(BaseModel):
    bill_id: str
    title: str
    introduced_date: Optional[str] = None
    status: Optional[str] = None
    url: Optional[str] = None
    sponsor: Optional[str] = None

class Vote(BaseModel):
    vote_id: str
    bill_id: Optional[str] = None
    bill_title: Optional[str] = None
    vote_date: Optional[str] = None
    question: Optional[str] = None
    result: Optional[str] = None
    chamber: str
    description: Optional[str] = None

# Database functions
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables for users and api configuration"""
    conn = get_db_connection()
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

# Initialize database on startup
init_db()

# Authentication functions
def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against a provided password."""
    return hash_password(plain_password) == hashed_password

def get_user(username: str):
    """Get a user by username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None

def authenticate_user(username: str, password: str):
    """Authenticate a user."""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user['password_hash']):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRATION_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except Exception:
        raise credentials_exception
    
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE id = ?", (token_data.user_id,)).fetchone()
    conn.close()
    
    if user is None:
        raise credentials_exception
    return dict(user)

# Direct API access functions
def get_congress_api_key():
    # Try to get from database first
    conn = get_db_connection()
    cursor = conn.cursor()
    config = cursor.execute("SELECT api_key FROM api_config LIMIT 1").fetchone()
    conn.close()
    
    if config and config['api_key']:
        return config['api_key']
    
    # Fall back to environment variable
    return API_KEY

def make_congress_api_request(endpoint, params=None):
    """Make a request to the Congress.gov API"""
    api_key = get_congress_api_key()
    if not api_key:
        logger.error("No API key configured for Congress API")
        raise HTTPException(status_code=500, detail="API key not configured")
    
    url = f"{API_BASE_URL}{endpoint}"
    
    # Add API key and format to params
    if params is None:
        params = {}
    params['api_key'] = api_key
    if 'format' not in params:
        params['format'] = 'json'
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"API request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")

# API Routes
@app.get("/")
def read_root():
    return {"message": "Welcome to the Watchdog API", "status": "running"}

# Auth endpoints
@app.post("/api/auth/register", response_model=User)
def register_user(user: UserCreate):
    """Register a new user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if username or email already exists
    existing_user = cursor.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?", 
        (user.username, user.email)
    ).fetchone()
    
    if existing_user:
        conn.close()
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Hash the password and insert the user
    password_hash = hash_password(user.password)
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, full_name, state, district) VALUES (?, ?, ?, ?, ?, ?)",
        (user.username, user.email, password_hash, user.full_name, user.state, user.district)
    )
    
    conn.commit()
    
    # Get the created user
    new_user_id = cursor.lastrowid
    new_user = cursor.execute("SELECT * FROM users WHERE id = ?", (new_user_id,)).fetchone()
    conn.close()
    
    user_dict = dict(new_user)
    return {
        "id": user_dict["id"],
        "username": user_dict["username"],
        "email": user_dict["email"],
        "full_name": user_dict["full_name"],
        "state": user_dict["state"],
        "district": user_dict["district"],
        "created_at": user_dict["created_at"],
        "is_active": bool(user_dict["is_active"])
    }

@app.post("/api/auth/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate and return a JWT token."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(user["id"])}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=User)
def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get the current authenticated user."""
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "state": current_user["state"],
        "district": current_user["district"],
        "created_at": current_user["created_at"],
        "is_active": bool(current_user["is_active"])
    }

@app.put("/api/users/me", response_model=User)
def update_user(user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Update the current user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = {}
    params = []
    
    if user_update.full_name is not None:
        updates["full_name"] = user_update.full_name
        params.append(user_update.full_name)
    
    if user_update.email is not None:
        # Check if email is already used by another user
        existing = cursor.execute(
            "SELECT id FROM users WHERE email = ? AND id != ?", 
            (user_update.email, current_user["id"])
        ).fetchone()
        
        if existing:
            conn.close()
            raise HTTPException(status_code=400, detail="Email already in use")
        
        updates["email"] = user_update.email
        params.append(user_update.email)
    
    if user_update.password is not None:
        updates["password_hash"] = hash_password(user_update.password)
        params.append(updates["password_hash"])
    
    if not updates:
        conn.close()
        return current_user
    
    # Construct the SQL query
    set_clause = ", ".join(f"{key} = ?" for key in updates)
    params.append(current_user["id"])
    
    cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", params)
    conn.commit()
    
    # Get the updated user
    updated_user = cursor.execute("SELECT * FROM users WHERE id = ?", (current_user["id"],)).fetchone()
    conn.close()
    
    user_dict = dict(updated_user)
    return {
        "id": user_dict["id"],
        "username": user_dict["username"],
        "email": user_dict["email"],
        "full_name": user_dict["full_name"],
        "state": user_dict["state"],
        "district": user_dict["district"],
        "created_at": user_dict["created_at"],
        "is_active": bool(user_dict["is_active"])
    }

# API configuration
@app.post("/api/config/api")
def set_api_config(config: ApiConfig):
    """Set the Congress.gov API configuration"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear existing and insert new
    cursor.execute("DELETE FROM api_config")
    cursor.execute(
        "INSERT INTO api_config (api_key, base_url) VALUES (?, ?)",
        (config.api_key, config.base_url)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": "API configuration updated successfully"}

@app.get("/api/config/api")
def get_api_config():
    """Get the Congress.gov API configuration status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    config = cursor.execute("SELECT id, base_url FROM api_config LIMIT 1").fetchone()
    conn.close()
    
    if config:
        return {
            "configured": True,
            "base_url": config['base_url']
        }
    else:
        return {
            "configured": False,
            "base_url": API_BASE_URL
        }

# Representatives endpoints - directly fetch from API, no local storage
@app.get("/api/representatives/house")
def get_house_representatives():
    """Get representatives from the House"""
    try:
        # Current congress number (118 for 2023-2024)
        congress = 118
        
        # Make API request
        data = make_congress_api_request(f"/congress/{congress}/members", {
            "chamber": "house"
        })
        
        # Extract and normalize members
        representatives = []
        for member in data.get("members", []):
            representatives.append({
                "congress_id": member.get("bioguideId"),
                "name": f"{member.get('lastName', '')}, {member.get('firstName', '')}",
                "state": member.get("state"),
                "district": member.get("district"),
                "party": member.get("party"),
                "chamber": "house"
            })
        
        return {"representatives": representatives}
    except Exception as e:
        logger.error(f"Error fetching House representatives: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/representatives/senate")
def get_senate_representatives():
    """Get representatives from the Senate"""
    try:
        # Current congress number (118 for 2023-2024)
        congress = 118
        
        # Make API request
        data = make_congress_api_request(f"/congress/{congress}/members", {
            "chamber": "senate"
        })
        
        # Extract and normalize members
        senators = []
        for member in data.get("members", []):
            senators.append({
                "congress_id": member.get("bioguideId"),
                "name": f"{member.get('lastName', '')}, {member.get('firstName', '')}",
                "state": member.get("state"),
                "district": None,  # Senators don't have districts
                "party": member.get("party"),
                "chamber": "senate"
            })
        
        return {"representatives": senators}
    except Exception as e:
        logger.error(f"Error fetching Senate representatives: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/representatives")
def get_all_representatives():
    """Get all representatives from both chambers"""
    house = get_house_representatives()["representatives"]
    senate = get_senate_representatives()["representatives"]
    return {"representatives": house + senate}

# Bills endpoints - directly fetch from API, no local storage
@app.get("/api/bills/recent")
def get_recent_bills(limit: int = 20):
    """Get recent bills from Congress"""
    try:
        # Calculate 30 days ago in ISO format
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Make API request
        data = make_congress_api_request("/bill", {
            "limit": limit,
            "sort": "updateDate+desc",
            "fromDateTime": thirty_days_ago
        })
        
        # Extract and normalize bills
        bills = []
        for bill in data.get("bills", []):
            sponsor_name = "Unknown"
            if bill.get("sponsors") and len(bill["sponsors"]) > 0:
                sponsor = bill["sponsors"][0]
                sponsor_name = f"{sponsor.get('lastName', '')}, {sponsor.get('firstName', '')}"
            
            bills.append({
                "bill_id": bill.get("billNumber"),
                "title": bill.get("title"),
                "introduced_date": bill.get("introducedDate"),
                "status": bill.get("latestAction", {}).get("text", "Unknown"),
                "url": bill.get("url"),
                "sponsor": sponsor_name
            })
        
        return {"bills": bills}
    except Exception as e:
        logger.error(f"Error fetching recent bills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Votes endpoints - directly fetch from API, no local storage
@app.get("/api/votes/recent")
def get_recent_votes(limit: int = 20):
    """Get recent votes from Congress"""
    try:
        # Calculate 30 days ago in ISO format
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Current congress number (118 for 2023-2024)
        congress = 118
        
        # Try different endpoints (some might not work)
        endpoints = [
            (f"/congress/{congress}/house/votes", "house"),
            (f"/congress/{congress}/senate/votes", "senate"),
            ("/vote", None)  # Generic endpoint
        ]
        
        for endpoint, chamber in endpoints:
            try:
                # Make API request
                params = {
                    "limit": limit,
                    "sort": "date+desc",
                    "fromDateTime": thirty_days_ago
                }
                
                if chamber:
                    params["chamber"] = chamber
                
                data = make_congress_api_request(endpoint, params)
                
                # If we got data, process it and return
                if "votes" in data:
                    votes = []
                    for vote in data.get("votes", []):
                        votes.append({
                            "vote_id": vote.get("voteNumber") or vote.get("rollCallNumber"),
                            "bill_id": vote.get("billNumber"),
                            "bill_title": vote.get("title") or vote.get("billTitle"),
                            "vote_date": vote.get("date") or vote.get("voteDate"),
                            "question": vote.get("question"),
                            "result": vote.get("result"),
                            "chamber": vote.get("chamber") or chamber,
                            "description": vote.get("description") or vote.get("voteTitle")
                        })
                    
                    return {"votes": votes}
            except Exception as e:
                logger.warning(f"Failed to get votes from {endpoint}: {str(e)}")
                continue
        
        # If we get here, none of the endpoints worked
        return {"votes": [], "error": "Could not retrieve votes from any endpoint"}
    except Exception as e:
        logger.error(f"Error fetching recent votes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# User saved items endpoints
@app.post("/api/users/me/representatives/{congress_id}")
def save_representative(congress_id: str, current_user: dict = Depends(get_current_user)):
    """Save a representative to the user's list"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO saved_representatives (user_id, congress_id) VALUES (?, ?)",
            (current_user["id"], congress_id)
        )
        conn.commit()
        conn.close()
        return {"message": "Representative saved successfully"}
    except sqlite3.IntegrityError:
        conn.close()
        return {"message": "Representative already saved"}

@app.delete("/api/users/me/representatives/{congress_id}")
def remove_saved_representative(congress_id: str, current_user: dict = Depends(get_current_user)):
    """Remove a representative from the user's list"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM saved_representatives WHERE user_id = ? AND congress_id = ?",
        (current_user["id"], congress_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": "Representative removed successfully"}

@app.get("/api/users/me/representatives")
def get_saved_representatives(current_user: dict = Depends(get_current_user)):
    """Get all representatives saved by the user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved = cursor.execute(
        "SELECT congress_id FROM saved_representatives WHERE user_id = ?", 
        (current_user["id"],)
    ).fetchall()
    
    conn.close()
    
    congress_ids = [item["congress_id"] for item in saved]
    
    if not congress_ids:
        return {"representatives": []}
    
    # Fetch details for all representatives
    all_reps = get_all_representatives()["representatives"]
    
    # Filter to only include saved representatives
    saved_reps = [rep for rep in all_reps if rep["congress_id"] in congress_ids]
    
    return {"representatives": saved_reps}

@app.post("/api/users/me/bills/{bill_id}")
def save_bill(bill_id: str, current_user: dict = Depends(get_current_user)):
    """Save a bill to the user's list"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO saved_bills (user_id, bill_id) VALUES (?, ?)",
            (current_user["id"], bill_id)
        )
        conn.commit()
        conn.close()
        return {"message": "Bill saved successfully"}
    except sqlite3.IntegrityError:
        conn.close()
        return {"message": "Bill already saved"}

@app.delete("/api/users/me/bills/{bill_id}")
def remove_saved_bill(bill_id: str, current_user: dict = Depends(get_current_user)):
    """Remove a bill from the user's list"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM saved_bills WHERE user_id = ? AND bill_id = ?",
        (current_user["id"], bill_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": "Bill removed successfully"}

@app.get("/api/users/me/bills")
def get_saved_bills(current_user: dict = Depends(get_current_user)):
    """Get all bills saved by the user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved = cursor.execute(
        "SELECT bill_id FROM saved_bills WHERE user_id = ?", 
        (current_user["id"],)
    ).fetchall()
    
    conn.close()
    
    bill_ids = [item["bill_id"] for item in saved]
    
    if not bill_ids:
        return {"bills": []}
    
    # Fetch details for each bill
    bills = []
    for bill_id in bill_ids:
        try:
            data = make_congress_api_request(f"/bill/{bill_id}")
            bill = data.get("bill", {})
            
            sponsor_name = "Unknown"
            if bill.get("sponsors") and len(bill["sponsors"]) > 0:
                sponsor = bill["sponsors"][0]
                sponsor_name = f"{sponsor.get('lastName', '')}, {sponsor.get('firstName', '')}"
            
            bills.append({
                "bill_id": bill.get("billNumber"),
                "title": bill.get("title"),
                "introduced_date": bill.get("introducedDate"),
                "status": bill.get("latestAction", {}).get("text", "Unknown"),
                "url": bill.get("url"),
                "sponsor": sponsor_name
            })
        except Exception as e:
            logger.warning(f"Error fetching bill {bill_id}: {str(e)}")
    
    return {"bills": bills}

@app.get("/api/representatives/member")
def get_member_details(state: str, district: Optional[str] = None):
    """Get details for a specific member by state and district"""
    try:
        # Current congress number (118 for 2023-2024)
        congress = 118
        
        # Determine chamber based on whether district is provided
        chamber = "house" if district else "senate"
        
        # Make API request
        data = make_congress_api_request(f"/congress/{congress}/members", {
            "chamber": chamber,
            "state": state
        })
        
        # Find the matching member
        member = None
        for m in data.get("members", []):
            if chamber == "house":
                if m.get("district") == district:
                    member = m
                    break
            else:
                member = m  # For senate, just take the first senator
                break
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        # Get additional member details
        member_id = member.get("bioguideId")
        if member_id:
            member_details = make_congress_api_request(f"/member/{member_id}")
            member.update(member_details.get("member", {}))
        
        return {
            "id": member.get("bioguideId"),
            "name": f"{member.get('lastName', '')}, {member.get('firstName', '')}",
            "state": member.get("state"),
            "district": member.get("district"),
            "party": member.get("party"),
            "chamber": chamber,
            "biography": member.get("biography"),
            "imageUrl": member.get("imageUrl"),
            "url": member.get("url")
        }
    except Exception as e:
        logger.error(f"Error fetching member details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/members/{member_id}/sponsored")
def get_member_sponsored_bills(member_id: str):
    """Get bills sponsored by a specific member"""
    try:
        # Current congress number (118 for 2023-2024)
        congress = 118
        
        # Make API request
        data = make_congress_api_request(f"/member/{member_id}/sponsored", {
            "congress": congress
        })
        
        # Extract and normalize bills
        bills = []
        for bill in data.get("bills", []):
            bills.append({
                "bill_id": bill.get("billNumber"),
                "title": bill.get("title"),
                "introduced_date": bill.get("introducedDate"),
                "status": bill.get("latestAction", {}).get("text", "Unknown"),
                "url": bill.get("url")
            })
        
        return {"bills": bills}
    except Exception as e:
        logger.error(f"Error fetching member sponsored bills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/members/{member_id}/cosponsored")
def get_member_cosponsored_bills(member_id: str):
    """Get bills cosponsored by a specific member"""
    try:
        # Current congress number (118 for 2023-2024)
        congress = 118
        
        # Make API request
        data = make_congress_api_request(f"/member/{member_id}/cosponsored", {
            "congress": congress
        })
        
        # Extract and normalize bills
        bills = []
        for bill in data.get("bills", []):
            bills.append({
                "bill_id": bill.get("billNumber"),
                "title": bill.get("title"),
                "introduced_date": bill.get("introducedDate"),
                "status": bill.get("latestAction", {}).get("text", "Unknown"),
                "url": bill.get("url")
            })
        
        return {"bills": bills}
    except Exception as e:
        logger.error(f"Error fetching member cosponsored bills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the server if executed directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True) 