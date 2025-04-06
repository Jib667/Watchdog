"""
Consolidated Core Module for Watchdog Backend

Includes configuration, security utilities, and static data.
"""

import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
import yaml # Add yaml import

from jose import JWTError, jwt
from passlib.context import CryptContext

# --- State Code Mapping --- #
STATE_CODE_TO_NAME = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
}

# Function to get the list of state names
def get_list_of_states() -> List[str]:
    """Returns a list of US state names."""
    return list(STATE_CODE_TO_NAME.values())

# --- Configuration Settings --- #

# Base directory determined relative to this file
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent # Assuming backend is one level down from project root
STATIC_DATA_DIR = APP_DIR / "static" / "congress_data" # Define static data dir
CONGRESS_DATA_FILE = STATIC_DATA_DIR / "legislators-current.yaml" # Define YAML file path

# Load environment variables (e.g., from .env file if using python-dotenv)
# Note: python-dotenv is not explicitly installed here, but often used.
# Ensure .env is in BACKEND_DIR or project root if used.

# Security configuration
JWT_SECRET = os.environ.get("JWT_SECRET", "default_super_secret_key_please_change") # CHANGE THIS IN .env!
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Admin configuration
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "watchdog123") # CHANGE THIS IN .env!

if JWT_SECRET == "default_super_secret_key_please_change":
    print("WARNING: Using default JWT_SECRET. Set a strong secret in your .env file!")
if ADMIN_PASSWORD == "watchdog123":
    print("WARNING: Using default ADMIN_PASSWORD. Set a strong password in your .env file!")


# --- Security Utilities --- #

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return its payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

# --- Static Congressional Data --- #

# Function to load and parse the congress data YAML file
def load_congress_data(file_path: Path) -> List[Dict[str, Any]]:
    """Loads legislator data from the specified YAML file."""
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        if not isinstance(data, list):
            print(f"Warning: Expected a list from {file_path}, but got {type(data)}. Returning empty list.")
            return []
        return data
    except FileNotFoundError:
        print(f"Error: Congress data file not found at {file_path}. Returning empty list.")
        return []
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {file_path}: {e}. Returning empty list.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while loading {file_path}: {e}. Returning empty list.")
        return []

# Load the raw data from the YAML file
raw_legislators_data = load_congress_data(CONGRESS_DATA_FILE)

# Function to generate a simple congress_id (replace with a more robust method if needed)
def _generate_congress_id(name, state, district=None):
    state = str(state) if state else ""
    name_part = ''.join(filter(str.isalnum, name)).upper()
    state_part = state.upper()
    if district and str(district).strip() and str(district).lower() != 'at-large':
        district_part = f"D{str(district).strip()}"
    else:
        district_part = "DAL" # Use DAL for At-Large or unspecified districts for representatives
    
    # Determine if senator (no district) or representative
    if district is None: # Senator
        return f"{state_part}_{name_part[:5]}"
    else: # Representative
        return f"{state_part}{district_part}_{name_part[:5]}"

# Function to generate image filename based on name
def _generate_image_filename(name):
    name_parts = name.split()
    if name_parts[-1] in ['Jr.', 'Sr.', 'I', 'II', 'III', 'IV']:
        name = ' '.join(name_parts[:-1])
    return name.lower().replace(' ', '_').replace('.', '').replace("'", "") + '.jpg'

# --- Representatives Data --- #
# representatives_raw: List[Dict[str, Any]] = [ ... ] # REMOVE HARDCODED LIST

# --- Senators Data --- #
# senators_raw: List[Dict[str, Any]] = [ ... ] # REMOVE HARDCODED LIST


# --- Processed Data --- #

def process_legislators(raw_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Processes raw legislator data into structured representatives and senators lists."""
    representatives = []
    senators = []

    # Add basic logging
    print(f"Processing {len(raw_data)} raw legislator entries.")

    if not raw_data:
        print("Warning: No raw legislator data loaded. Returning empty lists.")
        return {"representatives": [], "senators": []}

    processed_count = 0
    error_count = 0

    for entry in raw_data:
        try:
            # Find the most recent term marked as 'current' or the latest end date
            current_term = None
            latest_term_end_date = None

            if not entry.get('terms') or not isinstance(entry['terms'], list):
                # print(f"Skipping entry due to missing or invalid 'terms': {entry.get('id', {}).get('bioguide', 'N/A')}")
                error_count += 1
                continue # Skip if terms are missing or not a list

            sorted_terms = sorted(entry['terms'], key=lambda t: t.get('end', '0000-00-00'), reverse=True)

            # Prefer term explicitly marked as current, otherwise take the latest one
            # Sometimes 'current' isn't explicitly marked, rely on date sorting
            if sorted_terms:
                 current_term = sorted_terms[0] # Take the one with the latest end date

            if not current_term:
                # print(f"Skipping entry, could not determine current term: {entry.get('id', {}).get('bioguide', 'N/A')}")
                error_count += 1
                continue # Skip if no current term found

            # Extract common data
            name_data = entry.get('name', {})
            full_name = name_data.get('official_full') or f"{name_data.get('first', '')} {name_data.get('last', '')}".strip()
            if not full_name:
                 # print(f"Skipping entry due to missing name: {entry.get('id', {}).get('bioguide', 'N/A')}")
                 error_count += 1
                 continue # Skip if name is missing

            state_code = current_term.get('state')
            if not state_code or state_code not in STATE_CODE_TO_NAME:
                # print(f"Skipping entry due to invalid state code: {state_code} for {full_name}")
                error_count += 1
                continue # Skip if state is invalid

            state_name = STATE_CODE_TO_NAME[state_code]
            member_type = current_term.get('type')
            website = current_term.get('url')
            phone = current_term.get('phone')
            office = current_term.get('office')
            contact_form = current_term.get('contact_form')
            bioguide_id = entry.get('id', {}).get('bioguide')


            base_member_data = {
                "name": full_name,
                "state": state_name,
                "party": current_term.get('party'),
                "website": website,
                "image_url": f"/static/images/{_generate_image_filename(full_name)}",
                "phone": phone,
                "office_address": office,
                "contact_form": contact_form,
                "bioguide_id": bioguide_id,
                 # Add other relevant fields from current_term or entry if needed
                "term_start": current_term.get('start'),
                "term_end": current_term.get('end')
            }

            if member_type == 'rep':
                district = str(current_term.get('district', 'At-Large')).strip()
                if district.lower() == 'at-large' or not district.isdigit():
                     district_val = 'At-Large'
                else:
                     district_val = district

                congress_id = _generate_congress_id(full_name, state_code, district=district_val)
                representative_data = {
                    **base_member_data,
                    "district": district_val,
                    "congress_id": congress_id
                }
                representatives.append(representative_data)
                processed_count += 1
            elif member_type == 'sen':
                congress_id = _generate_congress_id(full_name, state_code, district=None) # district=None for senators
                senator_data = {
                    **base_member_data,
                    "congress_id": congress_id,
                    "state_rank": current_term.get('state_rank'),
                    "senate_class": current_term.get('class')
                }
                senators.append(senator_data)
                processed_count += 1
            # else:
                # print(f"Skipping entry with unknown type '{member_type}': {full_name}")
                # error_count += 1

        except Exception as e:
            # Log unexpected errors during processing of a single entry
            bioguide = entry.get('id', {}).get('bioguide', 'N/A')
            print(f"Error processing legislator entry {bioguide}: {e}")
            error_count += 1


    print(f"Finished processing. Processed: {processed_count}, Errors/Skipped: {error_count}")
    return {"representatives": representatives, "senators": senators}

# Process the loaded data
processed_data = process_legislators(raw_legislators_data)
ALL_REPRESENTATIVES = processed_data["representatives"]
ALL_SENATORS = processed_data["senators"]

# --- Helper Functions to Access Data --- #

# Sort representatives and senators once after loading
ALL_REPRESENTATIVES.sort(key=lambda x: (x['state'], int(x['district']) if x['district'].isdigit() else 999))
ALL_SENATORS.sort(key=lambda x: (x['state'], 0 if x.get('state_rank') == 'senior' else 1)) # Sort by state, then senior/junior

def get_all_representatives() -> List[Dict[str, Any]]:
    """Returns a list of all current representatives."""
    return ALL_REPRESENTATIVES

def get_all_senators() -> List[Dict[str, Any]]:
    """Returns a list of all current senators."""
    return ALL_SENATORS

def find_representative(state: str, district: Optional[str]):
    """Finds representative by state and district from static data.
       Handles both full state names and state codes.
    """
    # Normalize state input: if it's a code, convert to name
    normalized_state = STATE_CODE_TO_NAME.get(state.upper(), state)

    district_str = str(district).strip() if district else None
    # Normalize "At-Large" variations for district
    if district_str and district_str.lower() == 'at-large':
        district_str = 'At-Large'

    for rep in ALL_REPRESENTATIVES:
        # Check against normalized state name
        if rep['state'].lower() == normalized_state.lower():
            rep_district_str = str(rep.get('district')).strip() if rep.get('district') else None
            # Handle case variations and nulls for district comparison
            if str(rep_district_str).lower() == str(district_str).lower():
                return rep
            # Match "At-Large" rep if no specific district was provided by user
            if rep_district_str == 'At-Large' and not district_str:
                return rep
    return None

def find_senators(state: str) -> List[Dict[str, Any]]:
    """Finds senators by state from static data.
       Handles both full state names and state codes.
    """
    # Normalize state input: if it's a code, convert to name
    normalized_state = STATE_CODE_TO_NAME.get(state.upper(), state)

    # Return senators matching the normalized state name (case-insensitive)
    return [sen for sen in ALL_SENATORS if sen['state'].lower() == normalized_state.lower()]

def find_member_by_id(congress_id: str):
    """Finds a representative or senator by their generated congress_id."""
    # Check representatives first
    for rep in ALL_REPRESENTATIVES:
        if rep.get("congress_id") == congress_id:
            return {**rep, "member_type": "representative"}
    # Then check senators
    for sen in ALL_SENATORS:
        if sen.get("congress_id") == congress_id:
            return {**sen, "member_type": "senator"}
    return None # Not found