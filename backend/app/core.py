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

# --- Authoritative Main Committee List --- #
# Source of truth for main committee names and dropdown filtering
# IDs inferred from convention, membership files, and definition files
AUTHORITATIVE_MAIN_COMMITTEES = {
    # House Committees
    "HSAG": "House Committee on Agriculture",
    "HSAP": "House Committee on Appropriations",
    "HSAS": "House Committee on Armed Services",
    "HSBU": "House Committee on the Budget",
    "HSED": "House Committee on Education and Workforce",
    "HSIF": "House Committee on Energy and Commerce",
    "HSSO": "House Committee on Ethics",
    "HSBA": "House Committee on Financial Services",
    "HSFA": "House Committee on Foreign Affairs",
    "HSHM": "House Committee on Homeland Security",
    "HSHA": "House Committee on House Administration",
    "HSJU": "House Committee on the Judiciary",
    "HSII": "House Committee on Natural Resources",
    "HSGO": "House Committee on Oversight and Accountability", # Updated name
    "HSRU": "House Committee on Rules",
    "HSSY": "House Committee on Science, Space, and Technology",
    "HSSM": "House Committee on Small Business",
    "HSPW": "House Committee on Transportation and Infrastructure",
    "HSVR": "House Committee on Veterans' Affairs",
    "HSWM": "House Committee on Ways and Means",
    "HLIG": "House Permanent Select Committee on Intelligence",
    # Assuming HSCS based on user list, check committees-current.yaml if possible
    "HSCS": "House Select Committee on the Strategic Competition Between the United States and the Chinese Communist Party",

    # Senate Committees
    "SSAF": "Senate Committee on Agriculture, Nutrition, and Forestry",
    "SSAP": "Senate Committee on Appropriations",
    "SSAS": "Senate Committee on Armed Services",
    "SSBK": "Senate Committee on Banking, Housing, and Urban Affairs",
    "SSBU": "Senate Committee on the Budget",
    "SSCM": "Senate Committee on Commerce, Science, and Transportation",
    "SSEG": "Senate Committee on Energy and Natural Resources",
    "SSEV": "Senate Committee on Environment and Public Works",
    "SSFI": "Senate Committee on Finance",
    "SSFR": "Senate Committee on Foreign Relations",
    "SSHR": "Senate Committee on Health, Education, Labor, and Pensions",
    "SSGA": "Senate Committee on Homeland Security and Governmental Affairs",
    "SLIA": "Senate Committee on Indian Affairs",
    "SLAD": "Senate Committee on Rules and Administration", # Assuming SLAD, check yaml
    "SLET": "Senate Select Committee on Ethics",
    "SLIN": "Senate Select Committee on Intelligence",
    "SSSB": "Senate Committee on Small Business and Entrepreneurship",
    "SPAG": "Senate Special Committee on Aging",
    "SSVA": "Senate Committee on Veterans' Affairs",

    # Joint Committees (Using observed keys from logs/convention)
    "JECO": "Joint Economic Committee", # Assuming JECO, check yaml if possible
    "JSLC": "Joint Committee on the Library",
    "JSPR": "Joint Committee on Printing",
    "JSTX": "Joint Committee on Taxation",
}

# --- Configuration Settings --- #

# Base directory determined relative to this file
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent # Assuming backend is one level down from project root
STATIC_DATA_DIR = APP_DIR / "static" / "congress_data" # Define static data dir
CONGRESS_DATA_FILE = STATIC_DATA_DIR / "legislators-current.yaml" # Define YAML file path
COMMITTEE_DATA_FILE = STATIC_DATA_DIR / "committees-current.yaml"  # Committee data
COMMITTEE_MEMBERSHIP_FILE = STATIC_DATA_DIR / "committee-membership-current.yaml"  # Committee membership data

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

# Load committee data
def load_committee_data():
    """Load and process committee data"""
    try:
        # First load membership data since it has the keys we need to match
        with open(COMMITTEE_MEMBERSHIP_FILE, 'r') as f:
            membership_data = yaml.safe_load(f)
        
        # Now load committee definitions
        with open(COMMITTEE_DATA_FILE, 'r') as f:
            committee_definitions = yaml.safe_load(f)
        
        # Debug info
        print(f"Loaded raw membership data with {len(membership_data)} entries")
        print(f"Loaded raw committee definitions with {len(committee_definitions)} entries")
        
        # Create a mapping from thomas_id AS IT APPEARS in the definition file
        # Assumes thomas_id format is like 'SSAF', 'HSAG'
        thomas_to_committee = {}
        for committee_def_entry in committee_definitions:
            thomas_id_from_def = committee_def_entry.get('thomas_id')
            if thomas_id_from_def:
                thomas_to_committee[thomas_id_from_def] = committee_def_entry
        
        # Create the final committee map, keyed by membership_keys (e.g., SSAF, HSAG, SSAF13)
        committee_map = {}
        
        # Process each key from the membership data
        for membership_key in membership_data.keys():
            
            is_subcommittee = len(membership_key) > 4 and membership_key[4:].isdigit()
            
            if not is_subcommittee:
                # --- Main Committee Processing --- 
                lookup_key = membership_key # Use the membership key directly (e.g., SSAF, HSAG)
                committee_def = thomas_to_committee.get(lookup_key)
                
                # Get name from AUTHORITATIVE list first
                committee_name = AUTHORITATIVE_MAIN_COMMITTEES.get(lookup_key)
                committee_type = 'house' if lookup_key.startswith('H') else 'senate' # Default
                committee_url = ''
                
                if not committee_name:
                    # If not in authoritative list, try definition file
                    if committee_def and committee_def.get('name'):
                        committee_name = committee_def['name']
                        print(f"Warning: Committee '{lookup_key}' found in definitions but not authoritative list. Using defined name.")
                    else:
                        # Fallback to placeholder
                        committee_name = f"Committee {lookup_key}" 
                        print(f"Warning: Committee '{lookup_key}' not found in authoritative list or definitions. Using placeholder name.")
                
                # Get type/url from definition if available
                if committee_def:
                    if committee_def.get('type'): committee_type = committee_def['type']
                    if committee_def.get('url'): committee_url = committee_def['url']

                # Add/Update the main committee entry
                committee_map[membership_key] = {
                    'name': committee_name, # Use the authoritative/defined/placeholder name
                    'type': committee_type,
                    'url': committee_url,
                    'subcommittees': committee_map.get(membership_key, {}).get('subcommittees', {}) # Preserve existing subcommittees
                }
            else:
                # --- Subcommittee Processing --- 
                parent_key = membership_key[:4] # e.g., SSAF, HSAG
                suffix = membership_key[4:]
                
                # Lookup parent definition using the parent_key
                parent_lookup_key = parent_key
                parent_def = thomas_to_committee.get(parent_lookup_key)
                
                # Get PARENT name from AUTHORITATIVE list first
                parent_committee_full_name = AUTHORITATIVE_MAIN_COMMITTEES.get(parent_lookup_key)
                
                if not parent_committee_full_name:
                    # If parent not in authoritative list, try definition file
                    if parent_def and parent_def.get('name'):
                        parent_committee_full_name = parent_def['name']
                        print(f"Warning: Parent committee '{parent_lookup_key}' not in authoritative list. Using defined name for subcommittee processing.")
                    else:
                        # Fallback to placeholder ONLY if also not already in map
                        if parent_key in committee_map and committee_map[parent_key].get('name') != f"Committee {parent_key}":
                            parent_committee_full_name = committee_map[parent_key]['name']
                        else:
                            parent_committee_full_name = f"Committee {parent_key}" # Final fallback placeholder
                            print(f"Warning: Could not find ANY name for parent {parent_key} (Lookup: {parent_lookup_key}). Using placeholder for subcommittee.")
                
                # Ensure parent entry exists in committee_map (may create/update placeholder)
                if parent_key not in committee_map or committee_map[parent_key]['name'].startswith("Committee "):
                     parent_committee_type = 'house' if parent_key.startswith('H') else 'senate'
                     committee_map[parent_key] = {
                         'name': parent_committee_full_name, # Use the best name found
                         'type': parent_committee_type,
                         'url': parent_def.get('url', '') if parent_def else '',
                         'subcommittees': committee_map.get(parent_key, {}).get('subcommittees', {}) # Preserve subcommittees
                     }
                 
                # Get subcommittee short name from definition file
                subcom_short_name = f"Subcommittee {suffix}"
                subcom_def = None
                if parent_def and parent_def.get('subcommittees'):
                     for subcom in parent_def['subcommittees']:
                         if subcom.get('thomas_id') == suffix:
                             subcom_def = subcom
                             if subcom_def.get('name'): subcom_short_name = subcom_def['name']
                             break
                             
                # Add subcommittee details under the parent
                if 'subcommittees' not in committee_map[parent_key]:
                    committee_map[parent_key]['subcommittees'] = {}
                    
                committee_map[parent_key]['subcommittees'][membership_key] = {
                    'name': subcom_short_name,
                    'full_name': f"{parent_committee_full_name} - {subcom_short_name}" # Use authoritative parent name
                }
        
        # Print stats about what we processed
        committee_count = len(committee_map)
        subcommittee_count = sum(len(c.get('subcommittees', {})) for c in committee_map.values())
        print(f"Processed {committee_count} committees and {subcommittee_count} subcommittees")
        print(f"Committee map keys (sample): {list(committee_map.keys())[:5]}")
        print(f"Membership data keys (sample): {list(membership_data.keys())[:5]}")
        
        return {
            'committees': committee_map,
            'memberships': membership_data
        }
    except Exception as e:
        print(f"Error loading committee data: {e}")
        import traceback
        traceback.print_exc()
        return {'committees': {}, 'memberships': {}}

# Load committee data
committee_data = load_committee_data()

# Helper function for sorting committees
def _get_committee_sort_key(committee):
    """Generates a sort key for committee assignments.
    Sorts by leadership role first, then by rank.
    Handles potentially non-numeric ranks safely.
    """
    role_priority = 0 if committee.get('role') in ['Chairman', 'Ranking Member', 'Vice Chairman'] else 1
    
    rank_value = committee.get('rank', None) # Get rank, default to None if missing
    numeric_rank = 999 # Default rank for sorting if rank is missing or non-numeric
    
    # DEBUG: Print initial values
    # print(f"DEBUG Sort Key - Committee: {committee.get('committee_id', 'N/A')}, Role: {committee.get('role')}, Raw Rank Type: {type(rank_value)}, Raw Rank Value: {repr(rank_value)}")
    
    if rank_value is not None:
        rank_str = None
        try: 
            # Ensure conversion to string happens
            rank_str = str(rank_value)
            # print(f"DEBUG Sort Key - Converted Rank to String: {repr(rank_str)}, Type: {type(rank_str)}")
            
            # --- Explicit Type Check --- 
            if isinstance(rank_str, str):
                if rank_str.isdigit():
                    # print(f"DEBUG Sort Key - Rank String IS digit: {repr(rank_str)}")
                    try:
                        numeric_rank = int(rank_str)
                    except ValueError:
                        print(f"Warning: Could not convert rank '{rank_str}' to int despite passing isdigit(). Using 999.")
                        numeric_rank = 999
                else:
                    # print(f"DEBUG Sort Key - Rank String IS NOT digit: {repr(rank_str)}. Using 999.")
                    numeric_rank = 999 # Ensure default is set if not digit
            else:
                 # This case should ideally never happen if str() works as expected
                 print(f"Warning: str(rank_value) did not return a string for rank {repr(rank_value)}. Type was {type(rank_str)}. Using 999.")
                 numeric_rank = 999
                 
        except Exception as e:
             print(f"ERROR in _get_committee_sort_key converting/checking rank: {e} - Value was {repr(rank_value)}. Using 999.")
             numeric_rank = 999 # Ensure default is set on error
            
    # Final key
    sort_key = (role_priority, numeric_rank)
    # print(f"DEBUG Sort Key - Final Key for {committee.get('committee_id', 'N/A')}: {sort_key}")
    return sort_key

# Function to get committee assignments for a member by bioguide ID
def get_member_committees(bioguide_id):
    """Get committee assignments for a member by bioguide ID"""
    if not bioguide_id or not committee_data.get('memberships'): # Use .get for safety
        return []
        
    member_committees = []
    memberships = committee_data.get('memberships', {})
    committees_map = committee_data.get('committees', {})
    
    # Iterate through all committees in the memberships data
    for committee_id, members in memberships.items():
        # Ensure members is actually a list
        if not isinstance(members, list):
            # print(f"Warning: Skipping committee {committee_id} because members data is not a list: {type(members)}")
            continue
            
        for member in members:
            # Ensure member is a dictionary
            if not isinstance(member, dict):
                # print(f"Warning: Skipping member entry in {committee_id} because it is not a dictionary: {type(member)}")
                continue
                
            if member.get('bioguide') == bioguide_id:
                committee_info = {}
                parent_info = None
                subcom_info = None
                
                # Check if this is a subcommittee (has a parent committee)
                if len(committee_id) > 4:  # Subcommittees have longer IDs
                    parent_id = committee_id[:4]  # First 4 characters are the parent committee
                    
                    parent_data = committees_map.get(parent_id)
                    if parent_data:
                        parent_info = parent_data
                        subcom_info = parent_data.get('subcommittees', {}).get(committee_id)
                        
                    if parent_info and subcom_info:
                        committee_info = {
                            'committee_id': committee_id,
                            'name': subcom_info.get('full_name', f"{parent_info.get('name', parent_id)} - Subcommittee {committee_id[4:]}"),
                            'url': parent_info.get('url', ''),
                            'role': member.get('title', 'Member'),
                            'rank': member.get('rank'), # Keep original rank here
                            'is_subcommittee': True,
                            'parent_committee': parent_info.get('name', parent_id)
                        }
                    else: # Handle case where subcommittee exists in membership but not definitions
                         committee_info = {
                            'committee_id': committee_id,
                            'name': f"Subcommittee {committee_id}",
                            'url': '',
                            'role': member.get('title', 'Member'),
                            'rank': member.get('rank'),
                            'is_subcommittee': True,
                            'parent_committee': f"Committee {parent_id}"
                        }
                else:
                    # This is a full committee
                    committee_def = committees_map.get(committee_id)
                    if committee_def:
                        committee_info = {
                            'committee_id': committee_id,
                            'name': committee_def.get('name', f"Committee {committee_id}"),
                            'url': committee_def.get('url', ''),
                            'role': member.get('title', 'Member'),
                            'rank': member.get('rank'),
                            'is_subcommittee': False
                        }
                    else:
                        # Fallback for committees not in our definition file
                        committee_info = {
                            'committee_id': committee_id,
                            'name': f"Committee {committee_id}",
                            'url': '',
                            'role': member.get('title', 'Member'),
                            'rank': member.get('rank'),
                            'is_subcommittee': False
                        }
                
                if committee_info:
                    # Add the rank directly as it comes from the data
                    committee_info['rank'] = member.get('rank')
                    member_committees.append(committee_info)
    
    # Sort using the dedicated helper function
    try:
        member_committees.sort(key=_get_committee_sort_key)
    except Exception as e:
        print(f"Error during committee sort for bioguide {bioguide_id}: {e}")
        # Optionally print the list that failed to sort for debugging
        # print(f"Data that failed sorting: {member_committees}")
    
    return member_committees

# Get list of all committees for dropdown
def get_all_committees():
    """Get a list of all MAIN committees for the search dropdown, based on the authoritative list."""
    all_committees = []
    
    print(f"Generating dropdown list from AUTHORITATIVE_MAIN_COMMITTEES ({len(AUTHORITATIVE_MAIN_COMMITTEES)} entries).")
    
    # Iterate directly through the authoritative list
    for committee_id, committee_name in AUTHORITATIVE_MAIN_COMMITTEES.items():
        # Infer type from ID prefix for basic categorization if needed later
        committee_type = 'joint' # Default assumption for keys starting with J
        if committee_id.startswith('H'):
            committee_type = 'house'
        elif committee_id.startswith('S'):
            committee_type = 'senate'
            
        all_committees.append({
            'committee_id': committee_id, 
            'name': committee_name, # Use the authoritative name
            'type': committee_type 
        })

    # Sort by name
    all_committees.sort(key=lambda x: x.get('name', ''))
    print(f"RETURNING {len(all_committees)} committees for dropdown from authoritative list.")
    return all_committees

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

            if not entry.get('terms') or not isinstance(entry['terms'], list):
                error_count += 1
                continue # Skip if terms are missing or not a list

            sorted_terms = sorted(entry['terms'], key=lambda t: t.get('end', '0000-00-00'), reverse=True)

            # Prefer term explicitly marked as current, otherwise take the latest one
            # Sometimes 'current' isn't explicitly marked, rely on date sorting
            if sorted_terms:
                 current_term = sorted_terms[0] # Take the one with the latest end date

            if not current_term:
                error_count += 1
                continue # Skip if no current term found

            # Extract common data
            name_data = entry.get('name', {})
            full_name = name_data.get('official_full') or f"{name_data.get('first', '')} {name_data.get('last', '')}".strip()
            if not full_name:
                 error_count += 1
                 continue # Skip if name is missing

            state_code = current_term.get('state')
            if not state_code or state_code not in STATE_CODE_TO_NAME:
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
                "term_start": current_term.get('start'),
                "term_end": current_term.get('end')
            }

            if member_type == 'rep':
                # Convert district to string safely
                raw_district = current_term.get('district')
                district_val = 'At-Large'  # Default value
                
                if raw_district is not None:
                    if isinstance(raw_district, int):
                        district_val = str(raw_district)
                    elif isinstance(raw_district, str):
                        if raw_district.lower() == 'at-large':
                            district_val = 'At-Large'
                        else:
                            # Try to clean up and standardize the district value
                            district_val = raw_district.strip()

                congress_id = _generate_congress_id(full_name, state_code, district=district_val)
                representative_data = {
                    **base_member_data,
                    "district": district_val,
                    "congress_id": congress_id,
                    "committees": get_member_committees(bioguide_id) # Add committee data
                }
                representatives.append(representative_data)
                processed_count += 1
            elif member_type == 'sen':
                congress_id = _generate_congress_id(full_name, state_code, district=None) # district=None for senators
                senator_data = {
                    **base_member_data,
                    "congress_id": congress_id,
                    "state_rank": current_term.get('state_rank'),
                    "senate_class": current_term.get('class'),
                    "committees": get_member_committees(bioguide_id) # Add committee data
                }
                senators.append(senator_data)
                processed_count += 1

        except Exception as e:
            # Log unexpected errors during processing of a single entry
            bioguide = entry.get('id', {}).get('bioguide', 'N/A')
            print(f"--- Error processing legislator entry {bioguide} ---")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc() # Print full traceback
            # Log the problematic entry data for inspection
            try:
                import json
                print(f"Problematic entry data: {json.dumps(entry, indent=2)}")
            except Exception as json_err:
                print(f"Could not serialize entry data: {json_err}")
            print(f"--- End Error for {bioguide} ---")
            error_count += 1

    print(f"Finished processing. Processed: {processed_count}, Errors/Skipped: {error_count}")
    return {"representatives": representatives, "senators": senators}

# Process the loaded data
processed_data = process_legislators(raw_legislators_data)
ALL_REPRESENTATIVES = processed_data["representatives"]
ALL_SENATORS = processed_data["senators"]

# --- Helper Functions to Access Data --- #

# Safely sort representatives by state and district (handling all district formats)
def safe_district_sort(rep):
    """Sort function that properly handles district values safely"""
    state = rep.get('state', '')
    district = rep.get('district', 'At-Large')
    
    # At-Large districts come last within each state
    if district == 'At-Large':
        return (state, 9999)
    
    # Try to parse district as a number for proper sorting
    try:
        return (state, int(district))
    except (ValueError, TypeError):
        # If it's not a valid number, sort alphabetically
        return (state, district)

# Sort representatives and senators once after loading
ALL_REPRESENTATIVES.sort(key=safe_district_sort)
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