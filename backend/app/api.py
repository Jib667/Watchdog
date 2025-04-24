"""
Consolidated API Module for Watchdog Backend

Handles authentication, user management, and congress data endpoints.
"""

from datetime import timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlite3 import Row, IntegrityError
from pathlib import Path
import asyncio # For async lock if needed later, though sync cache is simpler here
from cachetools import TTLCache, cached
from threading import Lock

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
    STATE_CODE_TO_NAME,
    get_all_committees,
    get_member_committees,
    get_member_vote_history,
    get_all_representatives,
    get_all_senators,
    get_list_of_states,
    ADMIN_USERNAME,
    ADMIN_PASSWORD
)
from .db import get_db_connection, Token, TokenData, User, UserCreate, UserInDB

# --- In-Memory Caches --- #
# Cache holds up to 500 members' vote history for 1 hour (3600 seconds)
member_vote_cache = TTLCache(maxsize=500, ttl=3600)
# Using simple locks for thread-safety in sync context
member_cache_lock = Lock()

# Base path for congress data
CONGRESS_DATA_DIR = Path(__file__).parent / "static" / "congress_data" / "congress"

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
    district: Optional[str] = None,
    committee: Optional[str] = None
):
    """
    Search for congress members based on various criteria.
    
    Parameters:
    - name: Filter by name (partial match)
    - state: Filter by state (exact match)
    - party: Filter by party (exact match)
    - type: Filter by type (rep/sen)
    - district: Filter by district (for representatives only)
    - committee: Filter by committee ID
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
    
    # Debug info for committee filter
    if committee:
        print(f"Filtering by committee: {committee}")
        # Count members with committees data
        members_with_committees = sum(1 for m in results if m.get("committees"))
        print(f"Members with committee data: {members_with_committees} out of {len(results)}")
        
        # Check if any members have this specific committee
        matching_committee = []
        for m in results:
            if m.get("committees"):
                for c in m["committees"]:
                    if c.get("committee_id") == committee:
                        matching_committee.append(m.get("name", "Unknown"))
                        break
        
        if matching_committee:
            print(f"Found {len(matching_committee)} members on committee {committee}: {', '.join(matching_committee[:5])}" + 
                  (f"... and {len(matching_committee) - 5} more" if len(matching_committee) > 5 else ""))
        else:
            print(f"No members found for committee {committee}")
            
            # Check if this committee exists in our data
            from .core import committee_data
            if committee in committee_data['committees']:
                print(f"Committee exists in data but no members found: {committee_data['committees'][committee]['name']}")
            else:
                print(f"Committee ID not found in committee data: {committee}")
    
    # Apply filters
    filtered_results = []
    for member in results:
        # Name filter (case-insensitive partial match)
        if name and name.lower() not in member.get("name", "").lower():
            continue
        
        # State filter
        if normalized_state and normalized_state != member.get("state"):
            continue
        
        # Party filter
        if party and party != member.get("party"):
            continue
        
        # District filter (reps only)
        if district is not None and district != "" and member.get("district") != district:
            continue
            
        # Committee filter
        if committee and committee.strip():
            # Check if member belongs to specified committee
            has_committee = False
            member_committees = member.get("committees", [])
            
            # Enhanced committee matching to handle possible format differences
            for c in member_committees:
                member_committee_id = c.get("committee_id", "")
                
                # Direct match
                if member_committee_id == committee:
                    has_committee = True
                    print(f"MATCH: {member.get('name')} is on committee {committee}")
                    break
                    
                # Try case-insensitive match
                if member_committee_id.lower() == committee.lower():
                    has_committee = True
                    print(f"CASE MATCH: {member.get('name')} is on committee {committee}")
                    break
            
            if not has_committee and len(member_committees) > 0:
                # Print committees for debugging if the member has committees but not this one
                committee_ids = [c.get('committee_id', '') for c in member_committees]
                if len(committee_ids) <= 5:  # Only log if there aren't too many
                    print(f"NO MATCH: {member.get('name')} has committees {committee_ids} but not {committee}")
            
            if not has_committee:
                continue
        
        filtered_results.append(member)
    
    if committee:
        print(f"After committee filtering: {len(filtered_results)} members")
        
    return filtered_results

@router.get("/congress/committees", response_model=List[Dict[str, Any]], tags=["congress"])
async def get_committees():
    """Get all committees for dropdown selection"""
    return get_all_committees()

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

@router.get("/api/states", response_model=List[str], summary="Get List of States", description="Returns a list of US state names.")
def get_states():
    return get_list_of_states()

@router.get("/api/committees", response_model=List[Dict[str, Any]], summary="Get List of Committees", description="Returns a list of main congressional committees.")
def get_committees_list():
    return get_all_committees()

@router.get("/api/members/representatives", response_model=List[Dict[str, Any]], summary="Get All Representatives", description="Returns a list of all current US Representatives.")
def get_representatives():
    return get_all_representatives()

@router.get("/api/members/senators", response_model=List[Dict[str, Any]], summary="Get All Senators", description="Returns a list of all current US Senators.")
def get_senators():
    return get_all_senators()

@router.get("/api/members/search", response_model=List[Dict[str, Any]], summary="Search Members", description="Searches for members based on various criteria.")
def search_members_api(
    name: Optional[str] = Query(None, description="Filter by member name (partial match, case-insensitive)"),
    state: Optional[str] = Query(None, description="Filter by state (full name or abbreviation)"),
    party: Optional[str] = Query(None, description="Filter by party (e.g., 'Republican', 'Democrat', 'Independent')"),
    committee_id: Optional[str] = Query(None, description="Filter by committee ID (e.g., 'HSAG', 'SSFI')")
):
    reps = get_all_representatives()
    sens = get_all_senators()
    members = reps + sens
    results = []

    # Pre-fetch committee members if committee_id is provided
    committee_member_ids = set()
    if committee_id:
        # We need a way to get members *by* committee ID.
        # get_member_committees gets committees *for* a member.
        # Let's reuse the core logic for now, though inefficient.
        # A better approach would be to pre-process this mapping in core.py
        all_members_with_committees = [m for m in members if m.get('bioguide_id')]
        for member in all_members_with_committees:
            member_committees = get_member_committees(member['bioguide_id'])
            for committee in member_committees:
                # Check both main and subcommittee IDs
                if committee.get('committee_id') == committee_id:
                    committee_member_ids.add(member['bioguide_id'])
                    break
                # Check if parent committee ID matches for subcommittees
                parent_id = committee.get('committee_id', '')[:4]
                if committee.get('is_subcommittee') and parent_id == committee_id:
                     committee_member_ids.add(member['bioguide_id'])
                     break

    for member in members:
        match = True
        if name and name.lower() not in member.get('name', '').lower():
            match = False
        if state:
            # Check full state name or abbreviation
            normalized_state = state.strip().lower()
            member_state = member.get('state', '').lower()
            # Need state code mapping potentially, assume full name match for now
            # core.py has STATE_CODE_TO_NAME, could add NAME_TO_CODE or check both
            if normalized_state != member_state:
                # Add check for abbreviation if core provides mapping
                match = False # Placeholder
        if party and party.lower() != member.get('party', '').lower():
            match = False
        if committee_id and member.get('bioguide_id') not in committee_member_ids:
            match = False

        if match:
            results.append(member)

    # Limit results to avoid overwhelming the frontend?
    # return results[:50] # Example limit
    return results

@router.get("/api/members/id/{congress_id}", response_model=Dict[str, Any], summary="Get Member by Congress ID", description="Finds a specific member by their unique congress_id.")
def get_member_by_congress_id(congress_id: str):
    member = find_member_by_id(congress_id)
    if member:
        return member
    raise HTTPException(status_code=404, detail=f"Member with congress_id '{congress_id}' not found")

@router.get("/members/{bioguide_id}/votes", response_model=List[Dict[str, Any]], summary="Get Member Vote History", description="Retrieves the recorded vote history for a specific member by their bioguide_id.")
def get_votes_for_member(bioguide_id: str):
    """
    Fetches member vote history. Results are cached.
    """
    # Check cache first
    with member_cache_lock:
        cached_result = member_vote_cache.get(bioguide_id)
        if cached_result is not None: # Check for None explicitly in case cached result is []
            # print(f"[get_votes_for_member] Cache hit for bioguide_id: {bioguide_id}") # Debug log
            return cached_result

    # print(f"[get_votes_for_member] Cache miss for bioguide_id: {bioguide_id}. Fetching...") # Debug log
    # Get the basic history (list of votes with member's position)
    member_vote_history = get_member_vote_history(bioguide_id)

    if member_vote_history is None:
        # This can happen if the underlying function returns None (e.g., member not found)
         raise HTTPException(status_code=404, detail=f"Vote history not found for member {bioguide_id}")

    # Cache the result before returning (even if it's an empty list)
    with member_cache_lock:
        member_vote_cache[bioguide_id] = member_vote_history

    # print(f"[get_votes_for_member] Fetched {len(member_vote_history)} votes for {bioguide_id}. Caching result.") # Debug log
    return member_vote_history

# Removed old function filter_votes_by_type as filtering logic moved to frontend

@router.get("/api/secure-data", summary="Access Secure Data", description="Example of a protected endpoint requiring authentication.", tags=["auth"]) # Added tag for consistency
async def read_secure_data(current_user: UserInDB = Depends(get_current_user)):
    # Only accessible if get_current_user succeeds (token is valid)
    return {"message": f"Hello {current_user.username}! This data is secure.", "user_info": current_user}

# --- New Helper Functions for Vote Breakdown --- #

# @cached(vote_breakdown_cache, lock=breakdown_cache_lock)
# def _get_full_vote_data(vote_id: str) -> Optional[Dict]:
#     """
#     Loads the full data.json for a given vote_id.
#     Parses vote_id like 'h123-117.2022' or 's99-118.2023'.
#     Handles potential file not found or JSON errors.
#     Results are cached.
#     """
#     # print(f"[_get_full_vote_data] Attempting to load data for vote_id: {vote_id}") # Debug log
#     match = re.match(r"([hs])(\d+)-(\d+)\.(\d{4})", vote_id)
#     if not match:
#         print(f"Error: Could not parse vote_id format: {vote_id}")
#         return None
# 
#     chamber_code, vote_num, congress_num, year = match.groups()
#     chamber = chamber_code # Keep 'h' or 's'
# 
#     file_path = CONGRESS_DATA_DIR / congress_num / "votes" / year / f"{chamber}{vote_num}" / "data.json"
# 
#     if not file_path.is_file():
#         # print(f"Warning: Vote data file not found for {vote_id} at path: {file_path}") # Debug log
#         # Try common alternative for session folders (e.g. year-1 if congress spans two years)
#         alt_year = str(int(year) - 1)
#         alt_file_path = CONGRESS_DATA_DIR / congress_num / "votes" / alt_year / f"{chamber}{vote_num}" / "data.json"
#         if alt_file_path.is_file():
#             file_path = alt_file_path
#             # print(f"[_get_full_vote_data] Found vote data in alternative year folder: {file_path}") # Debug log
#         else:
#             print(f"Error: Vote data file not found for {vote_id} at {file_path} or {alt_file_path}")
#             return None # File doesn't exist
# 
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#         # print(f"[_get_full_vote_data] Successfully loaded data for {vote_id}") # Debug log
#         return data
#     except json.JSONDecodeError as e:
#         print(f"Error: Failed to parse JSON for vote {vote_id} at {file_path}: {e}")
#         return None
#     except Exception as e:
#         print(f"Error: Failed to read file for vote {vote_id} at {file_path}: {e}")
#         return None
# 
# def _calculate_party_breakdown(full_vote_data: Dict) -> Dict[str, Dict[str, int]]:
#     """
#     Calculates the vote breakdown by party from the full vote data.
#     Returns a dict like: {'R': {'yes': X, 'no': Y, ...}, 'D': {...}}
#     Uses party codes 'R', 'D', 'I' directly from the data.
#     """
#     breakdown = {}
#     if not full_vote_data or 'votes' not in full_vote_data:
#         return breakdown # Return empty if data is missing or invalid
# 
#     # Map JSON vote keys (Yea, Nay, etc.) to internal keys (yes, no, etc.)
#     vote_key_map = {
#         "Yea": "yes",
#         "Aye": "yes", # Handle variations
#         "Yes": "yes",
#         "Nay": "no",
#         "No": "no",
#         "Present": "present",
#         "Not Voting": "not_voting"
#     }
# 
#     for vote_position_key, members in full_vote_data['votes'].items():
#         internal_key = vote_key_map.get(vote_position_key)
#         if not internal_key:
#             # print(f"Warning: Unknown vote position key '{vote_position_key}' in vote data.") # Debug log
#             continue # Skip unknown vote types like 'Guilty', 'Not Guilty' for now
# 
#         if not isinstance(members, list):
#             # print(f"Warning: Expected list for vote position '{vote_position_key}', got {type(members)}.") # Debug log
#             continue # Skip if data format is unexpected
# 
#         for member in members:
#             # Add check: Ensure member is a dictionary before accessing .get()
#             if not isinstance(member, dict):
#                 # Optionally log this occurrence for debugging data inconsistencies
#                 # print(f"Warning: Expected dict for member, got {type(member)}: {member}") 
#                 continue
# 
#             party = member.get('party')
#             if not party:
#                 continue # Skip if member has no party listed
# 
#             # Ensure party entry exists
#             if party not in breakdown:
#                 breakdown[party] = {"yes": 0, "no": 0, "present": 0, "not_voting": 0}
# 
#             # Increment the count for the specific vote position
#             breakdown[party][internal_key] = breakdown[party].get(internal_key, 0) + 1
# 
#     # print(f"[_calculate_party_breakdown] Calculated breakdown: {breakdown}") # Debug log
#     return breakdown

# Make sure the main app includes this router
# Example in main.py: app.include_router(api.router, prefix="/api") 