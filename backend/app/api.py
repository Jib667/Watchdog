"""
Consolidated API Module for Watchdog Backend

Handles authentication, user management, and congress data endpoints.
"""

from datetime import timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlite3 import Row, IntegrityError

# Import from consolidated core and db modules
from .core import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    verify_password,
    get_password_hash,
    verify_token,
    ALL_REPRESENTATIVES as static_reps,
    ALL_SENATORS as static_sens,
    find_representative,
    find_senators,
    find_member_by_id,
    STATE_CODE_TO_NAME
)
from .db import get_db_connection, Token, TokenData, User, UserCreate, UserInDB

# --- Router Setup --- #
# Single router for all API endpoints
router = APIRouter()

# OAuth2 Scheme - Define once
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token") # Adjusted path

# --- Dependency for Current User --- #
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Dependency to get the current authenticated user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise credentials_exception

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        user_row = cursor.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    except Exception as e:
        # Log the error appropriately
        print(f"Database error fetching user: {e}") # Basic logging
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        if conn:
            conn.close()

    if user_row is None:
        raise credentials_exception

    # Convert Row to Pydantic model
    user_data = dict(user_row)
    return UserInDB(**user_data)

# --- Authentication Endpoints (/api/auth) --- #

@router.post("/auth/token", response_model=Token, tags=["auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get an access token."""
    conn = None
    user_row = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        user_row = cursor.execute(
            "SELECT * FROM users WHERE username = ?", (form_data.username,)
        ).fetchone()
    except Exception as e:
        print(f"Database error during login: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        if conn:
            conn.close()

    if not user_row or not verify_password(form_data.password, user_row["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_row["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- User Endpoints (/api/users) --- #

@router.post("/users/register", response_model=User, status_code=status.HTTP_201_CREATED, tags=["users"])
async def register_user(user: UserCreate):
    """Register a new user and link them to their congress members."""
    hashed_password = get_password_hash(user.password)

    # Find congress members from static data based on provided state/district
    rep = find_representative(user.state, user.district)
    sens = find_senators(user.state)

    rep_id = rep['congress_id'] if rep else None
    sen1_id = sens[0]['congress_id'] if len(sens) > 0 else None
    sen2_id = sens[1]['congress_id'] if len(sens) > 1 else None

    if not rep_id:
        print(f"Warning: Could not find representative for {user.state}/{user.district}")
    if not sen1_id:
        print(f"Warning: Could not find senators for {user.state}")

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO users (username, email, hashed_password, state, district,
                                representative_id, senator1_id, senator2_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user.username,
                user.email,
                hashed_password,
                user.state,
                user.district,
                rep_id,
                sen1_id,
                sen2_id
            )
        )
        conn.commit()
        user_id = cursor.lastrowid

    except IntegrityError as e:
        conn.rollback() # Rollback on integrity error
        detail = "Database integrity error."
        if "UNIQUE constraint failed: users.username" in str(e):
            detail = "Username already registered"
        elif "UNIQUE constraint failed: users.email" in str(e):
            detail = "Email already registered"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database error during registration: {e}")
        raise HTTPException(status_code=500, detail="Database error during registration")
    finally:
        if conn:
            conn.close()

    # Fetch the created user data to return
    # (Could construct manually but fetching ensures consistency)
    conn_fetch = None
    try:
        conn_fetch = get_db_connection()
        cursor_fetch = conn_fetch.cursor()
        new_user_row = cursor_fetch.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    except Exception as e:
        print(f"Database error fetching new user: {e}")
        # User was created, but we can't fetch them back - return minimal info or error?
        # For now, raise error, but might want to return basic info if needed.
        raise HTTPException(status_code=500, detail="Could not fetch newly created user")
    finally:
        if conn_fetch:
            conn_fetch.close()

    if not new_user_row:
        # Should not happen if insert succeeded and DB is consistent
        raise HTTPException(status_code=500, detail="Failed to retrieve user after creation")

    return UserInDB(**dict(new_user_row))

@router.get("/users/me", response_model=User, tags=["users"])
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """Get current logged-in user's information."""
    # current_user is already a Pydantic model UserInDB from the dependency
    return current_user

# --- Congress Static Data Endpoints (/api/congress) --- #

@router.get("/congress/static/representatives", response_model=List[Dict[str, Any]], tags=["congress"])
async def get_static_representatives():
    """Get the static list of all representatives."""
    return static_reps

@router.get("/congress/static/senators", response_model=List[Dict[str, Any]], tags=["congress"])
async def get_static_senators():
    """Get the static list of all senators."""
    return static_sens

# Removed old DB-querying congress endpoints 

# --- Congress Search/Member API --- #

@router.get("/congress/search", response_model=List[Dict[str, Any]], tags=["congress"])
async def search_members(
    name: Optional[str] = None,
    state: Optional[str] = None,
    party: Optional[str] = None,
    type: Optional[str] = None,
    district: Optional[str] = None
):
    """
    Search for congress members based on various criteria.
    
    Parameters:
    - name: Filter by name (partial match)
    - state: Filter by state (exact match)
    - party: Filter by party (exact match)
    - type: Filter by type (rep/sen)
    - district: Filter by district (for representatives only)
    """
    # Collect all members first based on type
    if type == "rep":
        results = static_reps.copy()
    elif type == "sen":
        results = static_sens.copy()
    else:
        # If no specific type, include both
        results = static_reps.copy() + static_sens.copy()
    
    # Normalize state if provided - handle both state codes and names
    normalized_state = None
    if state:
        # Check if it's a state code first
        normalized_state = STATE_CODE_TO_NAME.get(state.upper())
        # If not a code, use as is (it's a state name)
        if not normalized_state:
            normalized_state = state
    
    # Apply filters
    filtered_results = []
    for member in results:
        # Name filter (case-insensitive partial match)
        if name and name.lower() not in member["name"].lower():
            continue
            
        # State filter (case-insensitive match)
        if normalized_state and normalized_state.lower() != member["state"].lower():
            continue
            
        # Party filter (case-insensitive match)
        if party and party.lower() != member["party"].lower():
            continue
            
        # District filter (for representatives only)
        if district:
            # Only apply to representatives who have district field
            if "district" not in member:
                continue
            
            member_district = str(member["district"]).lower()
            search_district = str(district).lower()
            
            # Handle "At-Large" case - various forms
            if search_district in ["0", "at-large", "at large", "atl", "at-l"]:
                if member_district not in ["0", "at-large", "at large"]:
                    continue
            # Normal district number comparison
            elif member_district != search_district:
                continue
        
        filtered_results.append(member)
    
    return filtered_results


@router.get("/congress/member/{member_id}", response_model=Dict[str, Any], tags=["congress"])
async def get_member_by_id(member_id: str):
    """Get specific congress member by ID."""
    member = find_member_by_id(member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with id {member_id} not found"
        )
    return member 