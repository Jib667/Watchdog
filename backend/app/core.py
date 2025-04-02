"""
Consolidated Core Module for Watchdog Backend

Includes configuration, security utilities, and static data.
"""

import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from jose import JWTError, jwt
from passlib.context import CryptContext

# --- State Code Mapping --- #
# Basic mapping for lookup functions
# (Expand if more states are needed or use a library)
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
    # Add territories if needed, e.g., "DC": "District of Columbia"
}

# --- Configuration Settings --- #

# Base directory determined relative to this file
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent

# Load environment variables (e.g., from .env file if using python-dotenv)
# Note: python-dotenv is not explicitly installed here, but often used.
# Ensure .env is in BACKEND_DIR or project root if used.

# Security configuration
JWT_SECRET = os.environ.get("JWT_SECRET", "default_super_secret_key_please_change") # CHANGE THIS IN .env!
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Admin configuration (Potentially move to initial setup/DB seeding)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "watchdog123") # CHANGE THIS IN .env!

if JWT_SECRET == "default_super_secret_key_please_change":
    print("WARNING: Using default JWT_SECRET. Set a strong secret in your .env file!")
if ADMIN_PASSWORD == "watchdog123":
    print("WARNING: Using default ADMIN_PASSWORD. Set a strong password in your .env file!")


# --- Security Utilities --- #
# (Previously in security.py)

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
representatives_raw: List[Dict[str, Any]] = [
  {
    "name": "Jerry Carl",
    "state": "Alabama",
    "district": "1",
    "website": "https://carl.house.gov"
  },
  {
    "name": "Barry Moore",
    "state": "Alabama",
    "district": "2",
    "website": "https://barrymoore.house.gov"
  },
  {
    "name": "Mike Rogers",
    "state": "Alabama",
    "district": "3",
    "website": "https://mikerogers.house.gov"
  },
  {
    "name": "Robert Aderholt",
    "state": "Alabama",
    "district": "4",
    "website": "https://aderholt.house.gov"
  },
  {
    "name": "Dale Strong",
    "state": "Alabama",
    "district": "5",
    "website": "https://strong.house.gov"
  },
  {
    "name": "Gary Palmer",
    "state": "Alabama",
    "district": "6",
    "website": "https://palmer.house.gov"
  },
  {
    "name": "Terri Sewell",
    "state": "Alabama",
    "district": "7",
    "website": "https://sewell.house.gov"
  },
  {
    "name": "Mary Peltola",
    "state": "Alaska",
    "district": "At-Large",
    "website": "https://peltola.house.gov"
  },
  {
    "name": "David Schweikert",
    "state": "Arizona",
    "district": "1",
    "website": "https://schweikert.house.gov"
  },
  {
    "name": "Eli Crane",
    "state": "Arizona",
    "district": "2",
    "website": "https://crane.house.gov"
  },
  {
    "name": "Ruben Gallego",
    "state": "Arizona",
    "district": "3",
    "website": "https://rubengallego.house.gov"
  },
  {
    "name": "Greg Stanton",
    "state": "Arizona",
    "district": "4",
    "website": "https://stanton.house.gov"
  },
  {
    "name": "Andy Biggs",
    "state": "Arizona",
    "district": "5",
    "website": "https://biggs.house.gov"
  },
  {
    "name": "Juan Ciscomani",
    "state": "Arizona",
    "district": "6",
    "website": "https://ciscomani.house.gov"
  },
  {
    "name": "Raúl Grijalva",
    "state": "Arizona",
    "district": "7",
    "website": "https://grijalva.house.gov"
  },
  {
    "name": "Debbie Lesko",
    "state": "Arizona",
    "district": "8",
    "website": "https://lesko.house.gov"
  },
  {
    "name": "Paul Gosar",
    "state": "Arizona",
    "district": "9",
    "website": "https://gosar.house.gov"
  },
  {
    "name": "Rick Crawford",
    "state": "Arkansas",
    "district": "1",
    "website": "https://crawford.house.gov"
  },
  {
    "name": "French Hill",
    "state": "Arkansas",
    "district": "2",
    "website": "https://hill.house.gov"
  },
  {
    "name": "Steve Womack",
    "state": "Arkansas",
    "district": "3",
    "website": "https://womack.house.gov"
  },
  {
    "name": "Bruce Westerman",
    "state": "Arkansas",
    "district": "4",
    "website": "https://westerman.house.gov"
  },
  {
    "name": "Doug LaMalfa",
    "state": "California",
    "district": "1",
    "website": "https://lamalfa.house.gov"
  },
  {
    "name": "Jared Huffman",
    "state": "California",
    "district": "2",
    "website": "https://huffman.house.gov"
  },
  {
    "name": "Kevin Kiley",
    "state": "California",
    "district": "3",
    "website": "https://kiley.house.gov"
  },
  {
    "name": "Mike Thompson",
    "state": "California",
    "district": "4",
    "website": "https://mikethompson.house.gov"
  },
  {
    "name": "Tom McClintock",
    "state": "California",
    "district": "5",
    "website": "https://mcclintock.house.gov"
  },
  {
    "name": "Ami Bera",
    "state": "California",
    "district": "6",
    "website": "https://bera.house.gov"
  },
  {
    "name": "Doris Matsui",
    "state": "California",
    "district": "7",
    "website": "https://matsui.house.gov"
  },
  {
    "name": "John Garamendi",
    "state": "California",
    "district": "8",
    "website": "https://garamendi.house.gov"
  },
  {
    "name": "Josh Harder",
    "state": "California",
    "district": "9",
    "website": "https://harder.house.gov"
  },
  {
    "name": "Mark DeSaulnier",
    "state": "California",
    "district": "10",
    "website": "https://desaulnier.house.gov"
  },
  {
    "name": "Nancy Pelosi",
    "state": "California",
    "district": "11",
    "website": "https://pelosi.house.gov"
  },
  {
    "name": "Barbara Lee",
    "state": "California",
    "district": "12",
    "website": "https://lee.house.gov"
  },
  {
    "name": "John Duarte",
    "state": "California",
    "district": "13",
    "website": "https://duarte.house.gov"
  },
  {
    "name": "Eric Swalwell",
    "state": "California",
    "district": "14",
    "website": "https://swalwell.house.gov"
  },
  {
    "name": "Kevin Mullin",
    "state": "California",
    "district": "15",
    "website": "https://mullin.house.gov"
  },
  {
    "name": "Anna Eshoo",
    "state": "California",
    "district": "16",
    "website": "https://eshoo.house.gov"
  },
  {
    "name": "Ro Khanna",
    "state": "California",
    "district": "17",
    "website": "https://khanna.house.gov"
  },
  {
    "name": "Zoe Lofgren",
    "state": "California",
    "district": "18",
    "website": "https://lofgren.house.gov"
  },
  {
    "name": "Jimmy Panetta",
    "state": "California",
    "district": "19",
    "website": "https://panetta.house.gov"
  },
  {
    "name": "Kevin McCarthy",
    "state": "California",
    "district": "20",
    "website": "https://kevinmccarthy.house.gov"
  },
  {
    "name": "Jim Costa",
    "state": "California",
    "district": "21",
    "website": "https://costa.house.gov"
  },
  {
    "name": "Conor Lamb",
    "state": "California",
    "district": "22",
    "website": "https://lamb.house.gov"
  },
  {
    "name": "Jay Obernolte",
    "state": "California",
    "district": "23",
    "website": "https://obernolte.house.gov"
  },
  {
    "name": "Salud Carbajal",
    "state": "California",
    "district": "24",
    "website": "https://carbajal.house.gov"
  },
  {
    "name": "Raul Ruiz",
    "state": "California",
    "district": "25",
    "website": "https://ruiz.house.gov"
  },
  {
    "name": "Julia Brownley",
    "state": "California",
    "district": "26",
    "website": "https://brownley.house.gov"
  },
  {
    "name": "Mike Garcia",
    "state": "California",
    "district": "27",
    "website": "https://mikegarcia.house.gov"
  },
  {
    "name": "Judy Chu",
    "state": "California",
    "district": "28",
    "website": "https://chu.house.gov"
  },
  {
    "name": "Tony Cárdenas",
    "state": "California",
    "district": "29",
    "website": "https://cardenas.house.gov"
  },
  {
    "name": "Adam Schiff",
    "state": "California",
    "district": "30",
    "website": "https://schiff.house.gov"
  },
  {
    "name": "Grace Napolitano",
    "state": "California",
    "district": "31",
    "website": "https://napolitano.house.gov"
  },
  {
    "name": "Brad Sherman",
    "state": "California",
    "district": "32",
    "website": "https://sherman.house.gov"
  },
  {
    "name": "Pete Aguilar",
    "state": "California",
    "district": "33",
    "website": "https://aguilar.house.gov"
  },
  {
    "name": "Jimmy Gomez",
    "state": "California",
    "district": "34",
    "website": "https://gomez.house.gov"
  },
  {
    "name": "Norma Torres",
    "state": "California",
    "district": "35",
    "website": "https://torres.house.gov"
  },
  {
    "name": "Ted Lieu",
    "state": "California",
    "district": "36",
    "website": "https://lieu.house.gov"
  },
  {
    "name": "Sydney Kamlager-Dove",
    "state": "California",
    "district": "37",
    "website": "https://kamlager-dove.house.gov"
  },
  {
    "name": "Linda Sánchez",
    "state": "California",
    "district": "38",
    "website": "https://lindasanchez.house.gov"
  },
  {
    "name": "Mark Takano",
    "state": "California",
    "district": "39",
    "website": "https://takano.house.gov"
  },
  {
    "name": "Young Kim",
    "state": "California",
    "district": "40",
    "website": "https://youngkim.house.gov"
  },
  {
    "name": "Ken Calvert",
    "state": "California",
    "district": "41",
    "website": "https://calvert.house.gov"
  },
  {
    "name": "Robert Garcia",
    "state": "California",
    "district": "42",
    "website": "https://robertgarcia.house.gov"
  },
  {
    "name": "Maxine Waters",
    "state": "California",
    "district": "43",
    "website": "https://waters.house.gov"
  },
  {
    "name": "Nanette Barragán",
    "state": "California",
    "district": "44",
    "website": "https://barragan.house.gov"
  },
  {
    "name": "Katie Porter",
    "state": "California",
    "district": "45",
    "website": "https://porter.house.gov"
  },
  {
    "name": "Lou Correa",
    "state": "California",
    "district": "46",
    "website": "https://correa.house.gov"
  },
  {
    "name": "Darrell Issa",
    "state": "California",
    "district": "48",
    "website": "https://issa.house.gov"
  },
  {
    "name": "Mike Levin",
    "state": "California",
    "district": "49",
    "website": "https://mikelevin.house.gov"
  },
  {
    "name": "Scott Peters",
    "state": "California",
    "district": "50",
    "website": "https://scottpeters.house.gov"
  },
  {
    "name": "Sara Jacobs",
    "state": "California",
    "district": "51",
    "website": "https://sarajacobs.house.gov"
  },
  {
    "name": "Juan Vargas",
    "state": "California",
    "district": "52",
    "website": "https://vargas.house.gov"
  },
  {
    "name": "Diana DeGette",
    "state": "Colorado",
    "district": "1",
    "website": "https://degette.house.gov"
  },
  {
    "name": "Joe Neguse",
    "state": "Colorado",
    "district": "2",
    "website": "https://neguse.house.gov"
  },
  {
    "name": "Lauren Boebert",
    "state": "Colorado",
    "district": "3",
    "website": "https://boebert.house.gov"
  },
  {
    "name": "Ken Buck",
    "state": "Colorado",
    "district": "4",
    "website": "https://buck.house.gov"
  },
  {
    "name": "Doug Lamborn",
    "state": "Colorado",
    "district": "5",
    "website": "https://lamborn.house.gov"
  },
  {
    "name": "Jason Crow",
    "state": "Colorado",
    "district": "6",
    "website": "https://crow.house.gov"
  },
  {
    "name": "Brittany Pettersen",
    "state": "Colorado",
    "district": "7",
    "website": "https://pettersen.house.gov"
  },
  {
    "name": "Yadira Caraveo",
    "state": "Colorado",
    "district": "8",
    "website": "https://caraveo.house.gov"
  },
  {
    "name": "John Larson",
    "state": "Connecticut",
    "district": "1",
    "website": "https://larson.house.gov"
  },
  {
    "name": "Joe Courtney",
    "state": "Connecticut",
    "district": "2",
    "website": "https://courtney.house.gov"
  },
  {
    "name": "Rosa DeLauro",
    "state": "Connecticut",
    "district": "3",
    "website": "https://delauro.house.gov"
  },
  {
    "name": "Jim Himes",
    "state": "Connecticut",
    "district": "4",
    "website": "https://himes.house.gov"
  },
  {
    "name": "Jahana Hayes",
    "state": "Connecticut",
    "district": "5",
    "website": "https://hayes.house.gov"
  },
  {
    "name": "Lisa Blunt Rochester",
    "state": "Delaware",
    "district": "At-Large",
    "website": "https://bluntrochester.house.gov"
  },
  {
    "name": "Matt Gaetz",
    "state": "Florida",
    "district": "1",
    "website": "https://gaetz.house.gov"
  },
  {
    "name": "Neal Dunn",
    "state": "Florida",
    "district": "2",
    "website": "https://dunn.house.gov"
  },
  {
    "name": "Kat Cammack",
    "state": "Florida",
    "district": "3",
    "website": "https://cammack.house.gov"
  },
  {
    "name": "Aaron Bean",
    "state": "Florida",
    "district": "4",
    "website": "https://bean.house.gov"
  },
  {
    "name": "John Rutherford",
    "state": "Florida",
    "district": "5",
    "website": "https://rutherford.house.gov"
  },
  {
    "name": "Michael Waltz",
    "state": "Florida",
    "district": "6",
    "website": "https://waltz.house.gov"
  },
  {
    "name": "Cory Mills",
    "state": "Florida",
    "district": "7",
    "website": "https://mills.house.gov"
  },
  {
    "name": "Bill Posey",
    "state": "Florida",
    "district": "8",
    "website": "https://posey.house.gov"
  },
  {
    "name": "Darren Soto",
    "state": "Florida",
    "district": "9",
    "website": "https://soto.house.gov"
  },
  {
    "name": "Maxwell Frost",
    "state": "Florida",
    "district": "10",
    "website": "https://frost.house.gov"
  },
  {
    "name": "Daniel Webster",
    "state": "Florida",
    "district": "11",
    "website": "https://webster.house.gov"
  },
  {
    "name": "Gus Bilirakis",
    "state": "Florida",
    "district": "12",
    "website": "https://bilirakis.house.gov"
  },
  {
    "name": "Anna Paulina Luna",
    "state": "Florida",
    "district": "13",
    "website": "https://luna.house.gov"
  },
  {
    "name": "Kathy Castor",
    "state": "Florida",
    "district": "14",
    "website": "https://castor.house.gov"
  },
  {
    "name": "Laurel Lee",
    "state": "Florida",
    "district": "15",
    "website": "https://lee.house.gov"
  },
  {
    "name": "Vern Buchanan",
    "state": "Florida",
    "district": "16",
    "website": "https://buchanan.house.gov"
  },
  {
    "name": "Greg Steube",
    "state": "Florida",
    "district": "17",
    "website": "https://steube.house.gov"
  },
  {
    "name": "Scott Franklin",
    "state": "Florida",
    "district": "18",
    "website": "https://franklin.house.gov"
  },
  {
    "name": "Byron Donalds",
    "state": "Florida",
    "district": "19",
    "website": "https://donalds.house.gov"
  },
  {
    "name": "Sheila Cherfilus-McCormick",
    "state": "Florida",
    "district": "20",
    "website": "https://cherfilus-mccormick.house.gov"
  },
  {
    "name": "Brian Mast",
    "state": "Florida",
    "district": "21",
    "website": "https://mast.house.gov"
  },
  {
    "name": "Lois Frankel",
    "state": "Florida",
    "district": "22",
    "website": "https://frankel.house.gov"
  },
  {
    "name": "Jared Moskowitz",
    "state": "Florida",
    "district": "23",
    "website": "https://moskowitz.house.gov"
  },
  {
    "name": "Frederica Wilson",
    "state": "Florida",
    "district": "24",
    "website": "https://wilson.house.gov"
  },
  {
    "name": "Debbie Wasserman Schultz",
    "state": "Florida",
    "district": "25",
    "website": "https://wassermanschultz.house.gov"
  },
  {
    "name": "Mario Díaz-Balart",
    "state": "Florida",
    "district": "26",
    "website": "https://diaz-balart.house.gov"
  },
  {
    "name": "Maria Elvira Salazar",
    "state": "Florida",
    "district": "27",
    "website": "https://salazar.house.gov"
  },
  {
    "name": "Carlos Giménez",
    "state": "Florida",
    "district": "28",
    "website": "https://gimenez.house.gov"
  },
  {
    "name": "Buddy Carter",
    "state": "Georgia",
    "district": "1",
    "website": "https://buddycarter.house.gov"
  },
  {
    "name": "Sanford Bishop",
    "state": "Georgia",
    "district": "2",
    "website": "https://bishop.house.gov"
  },
  {
    "name": "Drew Ferguson",
    "state": "Georgia",
    "district": "3",
    "website": "https://ferguson.house.gov"
  },
  {
    "name": "Hank Johnson",
    "state": "Georgia",
    "district": "4",
    "website": "https://hankjohnson.house.gov"
  },
  {
    "name": "Nikema Williams",
    "state": "Georgia",
    "district": "5",
    "website": "https://nikemawilliams.house.gov"
  },
  {
    "name": "Rich McCormick",
    "state": "Georgia",
    "district": "6",
    "website": "https://mccormick.house.gov"
  },
  {
    "name": "Lucy McBath",
    "state": "Georgia",
    "district": "7",
    "website": "https://mcbath.house.gov"
  },
  {
    "name": "Austin Scott",
    "state": "Georgia",
    "district": "8",
    "website": "https://austinscott.house.gov"
  },
  {
    "name": "Andrew Clyde",
    "state": "Georgia",
    "district": "9",
    "website": "https://clyde.house.gov"
  },
  {
    "name": "Mike Collins",
    "state": "Georgia",
    "district": "10",
    "website": "https://collins.house.gov"
  },
  {
    "name": "Barry Loudermilk",
    "state": "Georgia",
    "district": "11",
    "website": "https://loudermilk.house.gov"
  },
  {
    "name": "Rick Allen",
    "state": "Georgia",
    "district": "12",
    "website": "https://allen.house.gov"
  },
  {
    "name": "David Scott",
    "state": "Georgia",
    "district": "13",
    "website": "https://davidscott.house.gov"
  },
  {
    "name": "Marjorie Taylor Greene",
    "state": "Georgia",
    "district": "14",
    "website": "https://greene.house.gov"
  },
  {
    "name": "Ed Case",
    "state": "Hawaii",
    "district": "1",
    "website": "https://case.house.gov"
  },
  {
    "name": "Jill Tokuda",
    "state": "Hawaii",
    "district": "2",
    "website": "https://tokuda.house.gov"
  },
  {
    "name": "Russ Fulcher",
    "state": "Idaho",
    "district": "1",
    "website": "https://fulcher.house.gov"
  },
  {
    "name": "Mike Simpson",
    "state": "Idaho",
    "district": "2",
    "website": "https://simpson.house.gov"
  },
  {
    "name": "Jonathan Jackson",
    "state": "Illinois",
    "district": "1",
    "website": "https://jackson.house.gov"
  },
  {
    "name": "Robin Kelly",
    "state": "Illinois",
    "district": "2",
    "website": "https://robinkelly.house.gov"
  },
  {
    "name": "Delia Ramirez",
    "state": "Illinois",
    "district": "3",
    "website": "https://ramirez.house.gov"
  },
  {
    "name": "Chuy García",
    "state": "Illinois",
    "district": "4",
    "website": "https://chuygarcia.house.gov"
  },
  {
    "name": "Mike Quigley",
    "state": "Illinois",
    "district": "5",
    "website": "https://quigley.house.gov"
  },
  {
    "name": "Sean Casten",
    "state": "Illinois",
    "district": "6",
    "website": "https://casten.house.gov"
  },
  {
    "name": "Danny Davis",
    "state": "Illinois",
    "district": "7",
    "website": "https://davisdanny.house.gov"
  },
  {
    "name": "Raja Krishnamoorthi",
    "state": "Illinois",
    "district": "8",
    "website": "https://krishnamoorthi.house.gov"
  },
  {
    "name": "Jan Schakowsky",
    "state": "Illinois",
    "district": "9",
    "website": "https://schakowsky.house.gov"
  },
  {
    "name": "Brad Schneider",
    "state": "Illinois",
    "district": "10",
    "website": "https://schneider.house.gov"
  },
  {
    "name": "Bill Foster",
    "state": "Illinois",
    "district": "11",
    "website": "https://foster.house.gov"
  },
  {
    "name": "Mike Bost",
    "state": "Illinois",
    "district": "12",
    "website": "https://bost.house.gov"
  },
  {
    "name": "Nikki Budzinski",
    "state": "Illinois",
    "district": "13",
    "website": "https://budzinski.house.gov"
  },
  {
    "name": "Lauren Underwood",
    "state": "Illinois",
    "district": "14",
    "website": "https://underwood.house.gov"
  },
  {
    "name": "Mary Miller",
    "state": "Illinois",
    "district": "15",
    "website": "https://marymiller.house.gov"
  },
  {
    "name": "Darin LaHood",
    "state": "Illinois",
    "district": "16",
    "website": "https://lahood.house.gov"
  },
  {
    "name": "Eric Sorensen",
    "state": "Illinois",
    "district": "17",
    "website": "https://sorensen.house.gov"
  },
  {
    "name": "Frank Mrvan",
    "state": "Indiana",
    "district": "1",
    "website": "https://mrvan.house.gov"
  },
  {
    "name": "Rudy Yakym",
    "state": "Indiana",
    "district": "2",
    "website": "https://yakym.house.gov"
  },
  {
    "name": "Jim Banks",
    "state": "Indiana",
    "district": "3",
    "website": "https://banks.house.gov"
  },
  {
    "name": "Jim Baird",
    "state": "Indiana",
    "district": "4",
    "website": "https://baird.house.gov"
  },
  {
    "name": "Victoria Spartz",
    "state": "Indiana",
    "district": "5",
    "website": "https://spartz.house.gov"
  },
  {
    "name": "Greg Pence",
    "state": "Indiana",
    "district": "6",
    "website": "https://pence.house.gov"
  },
  {
    "name": "André Carson",
    "state": "Indiana",
    "district": "7",
    "website": "https://carson.house.gov"
  },
  {
    "name": "Larry Bucshon",
    "state": "Indiana",
    "district": "8",
    "website": "https://bucshon.house.gov"
  },
  {
    "name": "Erin Houchin",
    "state": "Indiana",
    "district": "9",
    "website": "https://houchin.house.gov"
  },
  {
    "name": "Mariannette Miller-Meeks",
    "state": "Iowa",
    "district": "1",
    "website": "https://millermeeks.house.gov"
  },
  {
    "name": "Ashley Hinson",
    "state": "Iowa",
    "district": "2",
    "website": "https://hinson.house.gov"
  },
  {
    "name": "Zach Nunn",
    "state": "Iowa",
    "district": "3",
    "website": "https://nunn.house.gov"
  },
  {
    "name": "Randy Feenstra",
    "state": "Iowa",
    "district": "4",
    "website": "https://feenstra.house.gov"
  },
  {
    "name": "Tracy Mann",
    "state": "Kansas",
    "district": "1",
    "website": "https://mann.house.gov"
  },
  {
    "name": "Jake LaTurner",
    "state": "Kansas",
    "district": "2",
    "website": "https://laturner.house.gov"
  },
  {
    "name": "Sharice Davids",
    "state": "Kansas",
    "district": "3",
    "website": "https://davids.house.gov"
  },
  {
    "name": "Ron Estes",
    "state": "Kansas",
    "district": "4",
    "website": "https://estes.house.gov"
  },
  {
    "name": "James Comer",
    "state": "Kentucky",
    "district": "1",
    "website": "https://comer.house.gov"
  },
  {
    "name": "Brett Guthrie",
    "state": "Kentucky",
    "district": "2",
    "website": "https://guthrie.house.gov"
  },
  {
    "name": "Morgan McGarvey",
    "state": "Kentucky",
    "district": "3",
    "website": "https://mcgarvey.house.gov"
  },
  {
    "name": "Thomas Massie",
    "state": "Kentucky",
    "district": "4",
    "website": "https://massie.house.gov"
  },
  {
    "name": "Harold Rogers",
    "state": "Kentucky",
    "district": "5",
    "website": "https://halrogers.house.gov"
  },
  {
    "name": "Andy Barr",
    "state": "Kentucky",
    "district": "6",
    "website": "https://barr.house.gov"
  },
  {
    "name": "Steve Scalise",
    "state": "Louisiana",
    "district": "1",
    "website": "https://scalise.house.gov"
  },
  {
    "name": "Troy Carter",
    "state": "Louisiana",
    "district": "2",
    "website": "https://carter.house.gov"
  },
  {
    "name": "Clay Higgins",
    "state": "Louisiana",
    "district": "3",
    "website": "https://higgins.house.gov"
  },
  {
    "name": "Mike Johnson",
    "state": "Louisiana",
    "district": "4",
    "website": "https://mikejohnson.house.gov"
  },
  {
    "name": "Julia Letlow",
    "state": "Louisiana",
    "district": "5",
    "website": "https://letlow.house.gov"
  },
  {
    "name": "Garret Graves",
    "state": "Louisiana",
    "district": "6",
    "website": "https://graves.house.gov"
  },
  {
    "name": "Chellie Pingree",
    "state": "Maine",
    "district": "1",
    "website": "https://pingree.house.gov"
  },
  {
    "name": "Jared Golden",
    "state": "Maine",
    "district": "2",
    "website": "https://golden.house.gov"
  },
  {
    "name": "Andy Harris",
    "state": "Maryland",
    "district": "1",
    "website": "https://harris.house.gov"
  },
  {
    "name": "Dutch Ruppersberger",
    "state": "Maryland",
    "district": "2",
    "website": "https://ruppersberger.house.gov"
  },
  {
    "name": "John Sarbanes",
    "state": "Maryland",
    "district": "3",
    "website": "https://sarbanes.house.gov"
  },
  {
    "name": "Glenn Ivey",
    "state": "Maryland",
    "district": "4",
    "website": "https://ivey.house.gov"
  },
  {
    "name": "Steny Hoyer",
    "state": "Maryland",
    "district": "5",
    "website": "https://hoyer.house.gov"
  },
  {
    "name": "David Trone",
    "state": "Maryland",
    "district": "6",
    "website": "https://trone.house.gov"
  },
  {
    "name": "Kweisi Mfume",
    "state": "Maryland",
    "district": "7",
    "website": "https://mfume.house.gov"
  },
  {
    "name": "Jamie Raskin",
    "state": "Maryland",
    "district": "8",
    "website": "https://raskin.house.gov"
  },
  {
    "name": "Richard Neal",
    "state": "Massachusetts",
    "district": "1",
    "website": "https://neal.house.gov"
  },
  {
    "name": "Jim McGovern",
    "state": "Massachusetts",
    "district": "2",
    "website": "https://mcgovern.house.gov"
  },
  {
    "name": "Lori Trahan",
    "state": "Massachusetts",
    "district": "3",
    "website": "https://trahan.house.gov"
  },
  {
    "name": "Jake Auchincloss",
    "state": "Massachusetts",
    "district": "4",
    "website": "https://auchincloss.house.gov"
  },
  {
    "name": "Katherine Clark",
    "state": "Massachusetts",
    "district": "5",
    "website": "https://katherineclark.house.gov"
  },
  {
    "name": "Seth Moulton",
    "state": "Massachusetts",
    "district": "6",
    "website": "https://moulton.house.gov"
  },
  {
    "name": "Ayanna Pressley",
    "state": "Massachusetts",
    "district": "7",
    "website": "https://pressley.house.gov"
  },
  {
    "name": "Stephen Lynch",
    "state": "Massachusetts",
    "district": "8",
    "website": "https://lynch.house.gov"
  },
  {
    "name": "Bill Keating",
    "state": "Massachusetts",
    "district": "9",
    "website": "https://keating.house.gov"
  },
  {
    "name": "Jack Bergman",
    "state": "Michigan",
    "district": "1",
    "website": "https://bergman.house.gov"
  },
  {
    "name": "John Moolenaar",
    "state": "Michigan",
    "district": "2",
    "website": "https://moolenaar.house.gov"
  },
  {
    "name": "Hillary Scholten",
    "state": "Michigan",
    "district": "3",
    "website": "https://scholten.house.gov"
  },
  {
    "name": "Bill Huizenga",
    "state": "Michigan",
    "district": "4",
    "website": "https://huizenga.house.gov"
  },
  {
    "name": "Tim Walberg",
    "state": "Michigan",
    "district": "5",
    "website": "https://walberg.house.gov"
  },
  {
    "name": "Debbie Dingell",
    "state": "Michigan",
    "district": "6",
    "website": "https://dingell.house.gov"
  },
  {
    "name": "Elissa Slotkin",
    "state": "Michigan",
    "district": "7",
    "website": "https://slotkin.house.gov"
  },
  {
    "name": "Dan Kildee",
    "state": "Michigan",
    "district": "8",
    "website": "https://dankildee.house.gov"
  },
  {
    "name": "Lisa McClain",
    "state": "Michigan",
    "district": "9",
    "website": "https://mcclain.house.gov"
  },
  {
    "name": "John James",
    "state": "Michigan",
    "district": "10",
    "website": "https://james.house.gov"
  },
  {
    "name": "Haley Stevens",
    "state": "Michigan",
    "district": "11",
    "website": "https://stevens.house.gov"
  },
  {
    "name": "Rashida Tlaib",
    "state": "Michigan",
    "district": "12",
    "website": "https://tlaib.house.gov"
  },
  {
    "name": "Shri Thanedar",
    "state": "Michigan",
    "district": "13",
    "website": "https://thanedar.house.gov"
  },
  {
    "name": "Brad Finstad",
    "state": "Minnesota",
    "district": "1",
    "website": "https://finstad.house.gov"
  },
  {
    "name": "Angie Craig",
    "state": "Minnesota",
    "district": "2",
    "website": "https://craig.house.gov"
  },
  {
    "name": "Dean Phillips",
    "state": "Minnesota",
    "district": "3",
    "website": "https://phillips.house.gov"
  },
  {
    "name": "Betty McCollum",
    "state": "Minnesota",
    "district": "4",
    "website": "https://mccollum.house.gov"
  },
  {
    "name": "Ilhan Omar",
    "state": "Minnesota",
    "district": "5",
    "website": "https://omar.house.gov"
  },
  {
    "name": "Tom Emmer",
    "state": "Minnesota",
    "district": "6",
    "website": "https://emmer.house.gov"
  },
  {
    "name": "Michelle Fischbach",
    "state": "Minnesota",
    "district": "7",
    "website": "https://fischbach.house.gov"
  },
  {
    "name": "Pete Stauber",
    "state": "Minnesota",
    "district": "8",
    "website": "https://stauber.house.gov"
  },
  {
    "name": "Trent Kelly",
    "state": "Mississippi",
    "district": "1",
    "website": "https://trentkelly.house.gov"
  },
  {
    "name": "Bennie Thompson",
    "state": "Mississippi",
    "district": "2",
    "website": "https://benniethompson.house.gov"
  },
  {
    "name": "Michael Guest",
    "state": "Mississippi",
    "district": "3",
    "website": "https://guest.house.gov"
  },
  {
    "name": "Mike Ezell",
    "state": "Mississippi",
    "district": "4",
    "website": "https://ezell.house.gov"
  },
  {
    "name": "Cori Bush",
    "state": "Missouri",
    "district": "1",
    "website": "https://bush.house.gov"
  },
  {
    "name": "Ann Wagner",
    "state": "Missouri",
    "district": "2",
    "website": "https://wagner.house.gov"
  },
  {
    "name": "Blaine Luetkemeyer",
    "state": "Missouri",
    "district": "3",
    "website": "https://luetkemeyer.house.gov"
  },
  {
    "name": "Mark Alford",
    "state": "Missouri",
    "district": "4",
    "website": "https://alford.house.gov"
  },
  {
    "name": "Emanuel Cleaver",
    "state": "Missouri",
    "district": "5",
    "website": "https://cleaver.house.gov"
  },
  {
    "name": "Sam Graves",
    "state": "Missouri",
    "district": "6",
    "website": "https://graves.house.gov"
  },
  {
    "name": "Eric Burlison",
    "state": "Missouri",
    "district": "7",
    "website": "https://burlison.house.gov"
  },
  {
    "name": "Jason Smith",
    "state": "Missouri",
    "district": "8",
    "website": "https://adamsmith.house.gov"
  },
  {
    "name": "Ryan Zinke",
    "state": "Montana",
    "district": "1",
    "website": "https://zinke.house.gov"
  },
  {
    "name": "Matt Rosendale",
    "state": "Montana",
    "district": "2",
    "website": "https://rosendale.house.gov"
  },
  {
    "name": "Mike Flood",
    "state": "Nebraska",
    "district": "1",
    "website": "https://flood.house.gov"
  },
  {
    "name": "Don Bacon",
    "state": "Nebraska",
    "district": "2",
    "website": "https://bacon.house.gov"
  },
  {
    "name": "Adrian Smith",
    "state": "Nebraska",
    "district": "3",
    "website": "https://adriansmith.house.gov"
  },
  {
    "name": "Dina Titus",
    "state": "Nevada",
    "district": "1",
    "website": "https://titus.house.gov"
  },
  {
    "name": "Mark Amodei",
    "state": "Nevada",
    "district": "2",
    "website": "https://amodei.house.gov"
  },
  {
    "name": "Susie Lee",
    "state": "Nevada",
    "district": "3",
    "website": "https://susielee.house.gov"
  },
  {
    "name": "Steven Horsford",
    "state": "Nevada",
    "district": "4",
    "website": "https://horsford.house.gov"
  },
  {
    "name": "Chris Pappas",
    "state": "New Hampshire",
    "district": "1",
    "website": "https://pappas.house.gov"
  },
  {
    "name": "Ann Kuster",
    "state": "New Hampshire",
    "district": "2",
    "website": "https://kuster.house.gov"
  },
  {
    "name": "Donald Norcross",
    "state": "New Jersey",
    "district": "1",
    "website": "https://norcross.house.gov"
  },
  {
    "name": "Jeff Van Drew",
    "state": "New Jersey",
    "district": "2",
    "website": "https://vandrew.house.gov"
  },
  {
    "name": "Andy Kim",
    "state": "New Jersey",
    "district": "3",
    "website": "https://kim.house.gov"
  },
  {
    "name": "Chris Smith",
    "state": "New Jersey",
    "district": "4",
    "website": "https://chrissmith.house.gov"
  },
  {
    "name": "Josh Gottheimer",
    "state": "New Jersey",
    "district": "5",
    "website": "https://gottheimer.house.gov"
  },
  {
    "name": "Frank Pallone",
    "state": "New Jersey",
    "district": "6",
    "website": "https://pallone.house.gov"
  },
  {
    "name": "Thomas Kean",
    "state": "New Jersey",
    "district": "7",
    "website": "https://kean.house.gov"
  },
  {
    "name": "Rob Menendez",
    "state": "New Jersey",
    "district": "8",
    "website": "https://menendez.house.gov"
  },
  {
    "name": "Bill Pascrell",
    "state": "New Jersey",
    "district": "9",
    "website": "https://pascrell.house.gov"
  },
  {
    "name": "Donald Payne",
    "state": "New Jersey",
    "district": "10",
    "website": "https://payne.house.gov"
  },
  {
    "name": "Mikie Sherrill",
    "state": "New Jersey",
    "district": "11",
    "website": "https://sherrill.house.gov"
  },
  {
    "name": "Bonnie Watson Coleman",
    "state": "New Jersey",
    "district": "12",
    "website": "https://watsoncoleman.house.gov"
  },
  {
    "name": "Melanie Stansbury",
    "state": "New Mexico",
    "district": "1",
    "website": "https://stansbury.house.gov"
  },
  {
    "name": "Gabe Vasquez",
    "state": "New Mexico",
    "district": "2",
    "website": "https://vasquez.house.gov"
  },
  {
    "name": "Teresa Leger Fernandez",
    "state": "New Mexico",
    "district": "3",
    "website": "https://legerfernandez.house.gov"
  },
  {
    "name": "Claudia Tenney",
    "state": "New York",
    "district": "1",
    "website": "https://tenney.house.gov"
  },
  {
    "name": "Andrew Garbarino",
    "state": "New York",
    "district": "2",
    "website": "https://garbarino.house.gov"
  },
  {
    "name": "George Santos",
    "state": "New York",
    "district": "3",
    "website": "https://santos.house.gov"
  },
  {
    "name": "Anthony D'Esposito",
    "state": "New York",
    "district": "4",
    "website": "https://desposito.house.gov"
  },
  {
    "name": "Gregory Meeks",
    "state": "New York",
    "district": "5",
    "website": "https://meeks.house.gov"
  },
  {
    "name": "Grace Meng",
    "state": "New York",
    "district": "6",
    "website": "https://meng.house.gov"
  },
  {
    "name": "Nydia Velázquez",
    "state": "New York",
    "district": "7",
    "website": "https://velazquez.house.gov"
  },
  {
    "name": "Hakeem Jeffries",
    "state": "New York",
    "district": "8",
    "website": "https://jeffries.house.gov"
  },
  {
    "name": "Yvette Clarke",
    "state": "New York",
    "district": "9",
    "website": "https://clarke.house.gov"
  },
  {
    "name": "Dan Goldman",
    "state": "New York",
    "district": "10",
    "website": "https://goldman.house.gov"
  },
  {
    "name": "Nicole Malliotakis",
    "state": "New York",
    "district": "11",
    "website": "https://malliotakis.house.gov"
  },
  {
    "name": "Jerry Nadler",
    "state": "New York",
    "district": "12",
    "website": "https://nadler.house.gov"
  },
  {
    "name": "Adriano Espaillat",
    "state": "New York",
    "district": "13",
    "website": "https://espaillat.house.gov"
  },
  {
    "name": "Ritchie Torres",
    "state": "New York",
    "district": "15",
    "website": "https://torres.house.gov"
  },
  {
    "name": "Jamaal Bowman",
    "state": "New York",
    "district": "16",
    "website": "https://bowman.house.gov"
  },
  {
    "name": "Mike Lawler",
    "state": "New York",
    "district": "17",
    "website": "https://lawler.house.gov"
  },
  {
    "name": "Pat Ryan",
    "state": "New York",
    "district": "18",
    "website": "https://patryan.house.gov"
  },
  {
    "name": "Marc Molinaro",
    "state": "New York",
    "district": "19",
    "website": "https://molinaro.house.gov"
  },
  {
    "name": "Paul Tonko",
    "state": "New York",
    "district": "20",
    "website": "https://tonko.house.gov"
  },
  {
    "name": "Elise Stefanik",
    "state": "New York",
    "district": "21",
    "website": "https://stefanik.house.gov"
  },
  {
    "name": "Brandon Williams",
    "state": "New York",
    "district": "22",
    "website": "https://williams.house.gov"
  },
  {
    "name": "Nick Langworthy",
    "state": "New York",
    "district": "23",
    "website": "https://langworthy.house.gov"
  },
  {
    "name": "Claudia Tenney",
    "state": "New York",
    "district": "24",
    "website": "https://tenney.house.gov"
  },
  {
    "name": "Joseph Morelle",
    "state": "New York",
    "district": "25",
    "website": "https://morelle.house.gov"
  },
  {
    "name": "Deborah Ross",
    "state": "North Carolina",
    "district": "1",
    "website": "https://ross.house.gov"
  },
  {
    "name": "Deborah Ross",
    "state": "North Carolina",
    "district": "2",
    "website": "https://ross.house.gov"
  },
  {
    "name": "Greg Murphy",
    "state": "North Carolina",
    "district": "3",
    "website": "https://murphy.house.gov"
  },
  {
    "name": "Valerie Foushee",
    "state": "North Carolina",
    "district": "4",
    "website": "https://foushee.house.gov"
  },
  {
    "name": "Virginia Foxx",
    "state": "North Carolina",
    "district": "5",
    "website": "https://foxx.house.gov"
  },
  {
    "name": "Kathy Manning",
    "state": "North Carolina",
    "district": "6",
    "website": "https://manning.house.gov"
  },
  {
    "name": "David Rouzer",
    "state": "North Carolina",
    "district": "7",
    "website": "https://rouzer.house.gov"
  },
  {
    "name": "Dan Bishop",
    "state": "North Carolina",
    "district": "8",
    "website": "https://danbishop.house.gov"
  },
  {
    "name": "Richard Hudson",
    "state": "North Carolina",
    "district": "9",
    "website": "https://hudson.house.gov"
  },
  {
    "name": "Patrick McHenry",
    "state": "North Carolina",
    "district": "10",
    "website": "https://mchenry.house.gov"
  },
  {
    "name": "Chuck Edwards",
    "state": "North Carolina",
    "district": "11",
    "website": "https://edwards.house.gov"
  },
  {
    "name": "Alma Adams",
    "state": "North Carolina",
    "district": "12",
    "website": "https://adams.house.gov"
  },
  {
    "name": "Wiley Nickel",
    "state": "North Carolina",
    "district": "13",
    "website": "https://nickel.house.gov"
  },
  {
    "name": "Jeff Jackson",
    "state": "North Carolina",
    "district": "14",
    "website": "https://jeffjackson.house.gov"
  },
  {
    "name": "Kelly Armstrong",
    "state": "North Dakota",
    "district": "At-Large",
    "website": "https://armstrong.house.gov"
  },
  {
    "name": "Greg Landsman",
    "state": "Ohio",
    "district": "1",
    "website": "https://landsman.house.gov"
  },
  {
    "name": "Brad Wenstrup",
    "state": "Ohio",
    "district": "2",
    "website": "https://wenstrup.house.gov"
  },
  {
    "name": "Joyce Beatty",
    "state": "Ohio",
    "district": "3",
    "website": "https://beatty.house.gov"
  },
  {
    "name": "Jim Jordan",
    "state": "Ohio",
    "district": "4",
    "website": "https://jordan.house.gov"
  },
  {
    "name": "Bob Latta",
    "state": "Ohio",
    "district": "5",
    "website": "https://latta.house.gov"
  },
  {
    "name": "Bill Johnson",
    "state": "Ohio",
    "district": "6",
    "website": "https://billjohnson.house.gov"
  },
  {
    "name": "Max Miller",
    "state": "Ohio",
    "district": "7",
    "website": "https://maxmiller.house.gov"
  },
  {
    "name": "Warren Davidson",
    "state": "Ohio",
    "district": "8",
    "website": "https://davidson.house.gov"
  },
  {
    "name": "Marcy Kaptur",
    "state": "Ohio",
    "district": "9",
    "website": "https://kaptur.house.gov"
  },
  {
    "name": "Mike Turner",
    "state": "Ohio",
    "district": "10",
    "website": "https://turner.house.gov"
  },
  {
    "name": "Shontel Brown",
    "state": "Ohio",
    "district": "11",
    "website": "https://brown.house.gov"
  },
  {
    "name": "Troy Balderson",
    "state": "Ohio",
    "district": "12",
    "website": "https://balderson.house.gov"
  },
  {
    "name": "Emilia Sykes",
    "state": "Ohio",
    "district": "13",
    "website": "https://sykes.house.gov"
  },
  {
    "name": "David Joyce",
    "state": "Ohio",
    "district": "14",
    "website": "https://joyce.house.gov"
  },
  {
    "name": "Mike Carey",
    "state": "Ohio",
    "district": "15",
    "website": "https://carey.house.gov"
  },
  {
    "name": "Frank Lucas",
    "state": "Oklahoma",
    "district": "3",
    "website": "https://lucas.house.gov"
  },
  {
    "name": "Tom Cole",
    "state": "Oklahoma",
    "district": "4",
    "website": "https://cole.house.gov"
  },
  {
    "name": "Stephanie Bice",
    "state": "Oklahoma",
    "district": "5",
    "website": "https://bice.house.gov"
  },
  {
    "name": "Suzanne Bonamici",
    "state": "Oregon",
    "district": "1",
    "website": "https://bonamici.house.gov"
  },
  {
    "name": "Cliff Bentz",
    "state": "Oregon",
    "district": "2",
    "website": "https://bentz.house.gov"
  },
  {
    "name": "Earl Blumenauer",
    "state": "Oregon",
    "district": "3",
    "website": "https://blumenauer.house.gov"
  },
  {
    "name": "Val Hoyle",
    "state": "Oregon",
    "district": "4",
    "website": "https://hoyle.house.gov"
  },
  {
    "name": "Lori Chavez-DeRemer",
    "state": "Oregon",
    "district": "5",
    "website": "https://chavez-deremer.house.gov"
  },
  {
    "name": "Andrea Salinas",
    "state": "Oregon",
    "district": "6",
    "website": "https://salinas.house.gov"
  },
  {
    "name": "Brian Fitzpatrick",
    "state": "Pennsylvania",
    "district": "1",
    "website": "https://fitzpatrick.house.gov"
  },
  {
    "name": "Brendan Boyle",
    "state": "Pennsylvania",
    "district": "2",
    "website": "https://boyle.house.gov"
  },
  {
    "name": "Dwight Evans",
    "state": "Pennsylvania",
    "district": "3",
    "website": "https://evans.house.gov"
  },
  {
    "name": "Madeleine Dean",
    "state": "Pennsylvania",
    "district": "4",
    "website": "https://dean.house.gov"
  },
  {
    "name": "Mary Gay Scanlon",
    "state": "Pennsylvania",
    "district": "5",
    "website": "https://scanlon.house.gov"
  },
  {
    "name": "Chrissy Houlahan",
    "state": "Pennsylvania",
    "district": "6",
    "website": "https://houlahan.house.gov"
  },
  {
    "name": "Susan Wild",
    "state": "Pennsylvania",
    "district": "7",
    "website": "https://wild.house.gov"
  },
  {
    "name": "Matt Cartwright",
    "state": "Pennsylvania",
    "district": "8",
    "website": "https://cartwright.house.gov"
  },
  {
    "name": "Dan Meuser",
    "state": "Pennsylvania",
    "district": "9",
    "website": "https://meuser.house.gov"
  },
  {
    "name": "Scott Perry",
    "state": "Pennsylvania",
    "district": "10",
    "website": "https://perry.house.gov"
  },
  {
    "name": "Lloyd Smucker",
    "state": "Pennsylvania",
    "district": "11",
    "website": "https://smucker.house.gov"
  },
  {
    "name": "Summer Lee",
    "state": "Pennsylvania",
    "district": "12",
    "website": "https://summerlee.house.gov"
  },
  {
    "name": "John Joyce",
    "state": "Pennsylvania",
    "district": "13",
    "website": "https://johnjoyce.house.gov"
  },
  {
    "name": "Guy Reschenthaler",
    "state": "Pennsylvania",
    "district": "14",
    "website": "https://reschenthaler.house.gov"
  },
  {
    "name": "Glenn Thompson",
    "state": "Pennsylvania",
    "district": "15",
    "website": "https://thompson.house.gov"
  },
  {
    "name": "Mike Kelly",
    "state": "Pennsylvania",
    "district": "16",
    "website": "https://kelly.house.gov"
  },
  {
    "name": "Chris Deluzio",
    "state": "Pennsylvania",
    "district": "17",
    "website": "https://deluzio.house.gov"
  },
  {
    "name": "Seth Magaziner",
    "state": "Rhode Island",
    "district": "2",
    "website": "https://magaziner.house.gov"
  },
  {
    "name": "Nancy Mace",
    "state": "South Carolina",
    "district": "1",
    "website": "https://mace.house.gov"
  },
  {
    "name": "Joe Wilson",
    "state": "South Carolina",
    "district": "2",
    "website": "https://joewilson.house.gov"
  },
  {
    "name": "Jeff Duncan",
    "state": "South Carolina",
    "district": "3",
    "website": "https://jeffduncan.house.gov"
  },
  {
    "name": "William Timmons",
    "state": "South Carolina",
    "district": "4",
    "website": "https://timmons.house.gov"
  },
  {
    "name": "Ralph Norman",
    "state": "South Carolina",
    "district": "5",
    "website": "https://norman.house.gov"
  },
  {
    "name": "Jim Clyburn",
    "state": "South Carolina",
    "district": "6",
    "website": "https://clyburn.house.gov"
  },
  {
    "name": "Russell Fry",
    "state": "South Carolina",
    "district": "7",
    "website": "https://fry.house.gov"
  },
  {
    "name": "Dusty Johnson",
    "state": "South Dakota",
    "district": "At-Large",
    "website": "https://dustyjohnson.house.gov"
  },
  {
    "name": "Diana Harshbarger",
    "state": "Tennessee",
    "district": "1",
    "website": "https://harshbarger.house.gov"
  },
  {
    "name": "Tim Burchett",
    "state": "Tennessee",
    "district": "2",
    "website": "https://burchett.house.gov"
  },
  {
    "name": "Chuck Fleischmann",
    "state": "Tennessee",
    "district": "3",
    "website": "https://fleischmann.house.gov"
  },
  {
    "name": "Scott DesJarlais",
    "state": "Tennessee",
    "district": "4",
    "website": "https://desjarlais.house.gov"
  },
  {
    "name": "Andy Ogles",
    "state": "Tennessee",
    "district": "5",
    "website": "https://ogles.house.gov"
  },
  {
    "name": "John Rose",
    "state": "Tennessee",
    "district": "6",
    "website": "https://johnrose.house.gov"
  },
  {
    "name": "Mark Green",
    "state": "Tennessee",
    "district": "7",
    "website": "https://markgreen.house.gov"
  },
  {
    "name": "David Kustoff",
    "state": "Tennessee",
    "district": "8",
    "website": "https://kustoff.house.gov"
  },
  {
    "name": "Steve Cohen",
    "state": "Tennessee",
    "district": "9",
    "website": "https://cohen.house.gov"
  },
  {
    "name": "Morgan Luttrell",
    "state": "Texas",
    "district": "8",
    "website": "https://luttrell.house.gov"
  },
  {
    "name": "Al Green",
    "state": "Texas",
    "district": "9",
    "website": "https://algreen.house.gov"
  },
  {
    "name": "Michael McCaul",
    "state": "Texas",
    "district": "10",
    "website": "https://mccaul.house.gov"
  },
  {
    "name": "August Pfluger",
    "state": "Texas",
    "district": "11",
    "website": "https://pfluger.house.gov"
  },
  {
    "name": "Kay Granger",
    "state": "Texas",
    "district": "12",
    "website": "https://kaygranger.house.gov"
  },
  {
    "name": "Ronny Jackson",
    "state": "Texas",
    "district": "13",
    "website": "https://jackson.house.gov"
  },
  {
    "name": "Randy Weber",
    "state": "Texas",
    "district": "14",
    "website": "https://weber.house.gov"
  },
  {
    "name": "Monica De La Cruz",
    "state": "Texas",
    "district": "15",
    "website": "https://delacruz.house.gov"
  },
  {
    "name": "Veronica Escobar",
    "state": "Texas",
    "district": "16",
    "website": "https://escobar.house.gov"
  },
  {
    "name": "Pete Sessions",
    "state": "Texas",
    "district": "17",
    "website": "https://sessions.house.gov"
  },
  {
    "name": "Sheila Jackson Lee",
    "state": "Texas",
    "district": "18",
    "website": "https://jacksonlee.house.gov"
  },
  {
    "name": "Randy Neugebauer",
    "state": "Texas",
    "district": "19",
    "website": "https://neugebauer.house.gov"
  },
  {
    "name": "Joaquin Castro",
    "state": "Texas",
    "district": "20",
    "website": "https://castro.house.gov"
  },
  {
    "name": "Chip Roy",
    "state": "Texas",
    "district": "21",
    "website": "https://roy.house.gov"
  },
  {
    "name": "Tony Gonzales",
    "state": "Texas",
    "district": "23",
    "website": "https://gonzales.house.gov"
  },
  {
    "name": "Beth Van Duyne",
    "state": "Texas",
    "district": "24",
    "website": "https://vanduyne.house.gov"
  },
  {
    "name": "Roger Williams",
    "state": "Texas",
    "district": "25",
    "website": "https://williams.house.gov"
  },
  {
    "name": "Michael Burgess",
    "state": "Texas",
    "district": "26",
    "website": "https://burgess.house.gov"
  },
  {
    "name": "Michael Cloud",
    "state": "Texas",
    "district": "27",
    "website": "https://cloud.house.gov"
  },
  {
    "name": "Henry Cuellar",
    "state": "Texas",
    "district": "28",
    "website": "https://cuellar.house.gov"
  },
  {
    "name": "Sylvia Garcia",
    "state": "Texas",
    "district": "29",
    "website": "https://sylviagarcia.house.gov"
  },
  {
    "name": "Eddie Bernice Johnson",
    "state": "Texas",
    "district": "30",
    "website": "https://ebjohnson.house.gov"
  },
  {
    "name": "John Carter",
    "state": "Texas",
    "district": "31",
    "website": "https://carter.house.gov"
  },
  {
    "name": "Colin Allred",
    "state": "Texas",
    "district": "32",
    "website": "https://allred.house.gov"
  },
  {
    "name": "Marc Veasey",
    "state": "Texas",
    "district": "33",
    "website": "https://veasey.house.gov"
  },
  {
    "name": "Vicente Gonzalez",
    "state": "Texas",
    "district": "34",
    "website": "https://gonzalez.house.gov"
  },
  {
    "name": "Lloyd Doggett",
    "state": "Texas",
    "district": "35",
    "website": "https://doggett.house.gov"
  },
  {
    "name": "Brian Babin",
    "state": "Texas",
    "district": "36",
    "website": "https://babin.house.gov"
  },
  {
    "name": "Blake Moore",
    "state": "Utah",
    "district": "1",
    "website": "https://blakemoore.house.gov"
  },
  {
    "name": "Chris Stewart",
    "state": "Utah",
    "district": "2",
    "website": "https://stewart.house.gov"
  },
  {
    "name": "John Curtis",
    "state": "Utah",
    "district": "3",
    "website": "https://curtis.house.gov"
  },
  {
    "name": "Burgess Owens",
    "state": "Utah",
    "district": "4",
    "website": "https://owens.house.gov"
  },
  {
    "name": "Becca Balint",
    "state": "Vermont",
    "district": "At-Large",
    "website": "https://balint.house.gov"
  },
  {
    "name": "Rob Wittman",
    "state": "Virginia",
    "district": "1",
    "website": "https://wittman.house.gov"
  },
  {
    "name": "Jen Kiggans",
    "state": "Virginia",
    "district": "2",
    "website": "https://kiggans.house.gov"
  },
  {
    "name": "Bobby Scott",
    "state": "Virginia",
    "district": "3",
    "website": "https://bobbyscott.house.gov"
  },
  {
    "name": "Jennifer McClellan",
    "state": "Virginia",
    "district": "4",
    "website": "https://mcclellan.house.gov"
  },
  {
    "name": "Bob Good",
    "state": "Virginia",
    "district": "5",
    "website": "https://good.house.gov"
  },
  {
    "name": "Ben Cline",
    "state": "Virginia",
    "district": "6",
    "website": "https://cline.house.gov"
  },
  {
    "name": "Abigail Spanberger",
    "state": "Virginia",
    "district": "7",
    "website": "https://spanberger.house.gov"
  },
  {
    "name": "Don Beyer",
    "state": "Virginia",
    "district": "8",
    "website": "https://beyer.house.gov"
  },
  {
    "name": "Morgan Griffith",
    "state": "Virginia",
    "district": "9",
    "website": "https://griffith.house.gov"
  },
  {
    "name": "Jennifer Wexton",
    "state": "Virginia",
    "district": "10",
    "website": "https://wexton.house.gov"
  },
  {
    "name": "Gerry Connolly",
    "state": "Virginia",
    "district": "11",
    "website": "https://connolly.house.gov"
  },
  {
    "name": "Marie Gluesenkamp Perez",
    "state": "Washington",
    "district": "3",
    "website": "https://gluesenkampperez.house.gov"
  },
  {
    "name": "Dan Newhouse",
    "state": "Washington",
    "district": "4",
    "website": "https://newhouse.house.gov"
  },
  {
    "name": "Cathy McMorris Rodgers",
    "state": "Washington",
    "district": "5",
    "website": "https://mcmorrisrodgers.house.gov"
  },
  {
    "name": "Derek Kilmer",
    "state": "Washington",
    "district": "6",
    "website": "https://kilmer.house.gov"
  },
  {
    "name": "Pramila Jayapal",
    "state": "Washington",
    "district": "7",
    "website": "https://jayapal.house.gov"
  },
  {
    "name": "Kim Schrier",
    "state": "Washington",
    "district": "8",
    "website": "https://schrier.house.gov"
  },
  {
    "name": "Adam Smith",
    "state": "Washington",
    "district": "9",
    "website": "https://adamsmith.house.gov"
  },
  {
    "name": "Marilyn Strickland",
    "state": "Washington",
    "district": "10",
    "website": "https://strickland.house.gov"
  },
  {
    "name": "Carol Miller",
    "state": "West Virginia",
    "district": "1",
    "website": "https://miller.house.gov"
  },
  {
    "name": "Alex Mooney",
    "state": "West Virginia",
    "district": "2",
    "website": "https://mooney.house.gov"
  },
  {
    "name": "Bryan Steil",
    "state": "Wisconsin",
    "district": "1",
    "website": "https://steil.house.gov"
  },
  {
    "name": "Mark Pocan",
    "state": "Wisconsin",
    "district": "2",
    "website": "https://pocan.house.gov"
  },
  {
    "name": "Derrick Van Orden",
    "state": "Wisconsin",
    "district": "3",
    "website": "https://vanorden.house.gov"
  },
  {
    "name": "Gwen Moore",
    "state": "Wisconsin",
    "district": "4",
    "website": "https://gwenmoore.house.gov"
  },
  {
    "name": "Scott Fitzgerald",
    "state": "Wisconsin",
    "district": "5",
    "website": "https://fitzgerald.house.gov"
  },
  {
    "name": "Glenn Grothman",
    "state": "Wisconsin",
    "district": "6",
    "website": "https://grothman.house.gov"
  },
  {
    "name": "Tom Tiffany",
    "state": "Wisconsin",
    "district": "7",
    "website": "https://tiffany.house.gov"
  },
  {
    "name": "Harriet Hageman",
    "state": "Wyoming",
    "district": "At-Large",
    "website": "https://hageman.house.gov"
  }
]

representatives: List[Dict[str, Any]] = [
    {
        "congress_id": _generate_congress_id(rep["name"], rep["state"], rep.get("district")),
        "image_filename": _generate_image_filename(rep["name"]),
        **rep
    }
    for rep in representatives_raw
]

# --- Senators Data --- #
senators_raw: List[Dict[str, Any]] = [
  {
    "name": "Tommy Tuberville",
    "state": "Alabama",
    "website": "https://www.tuberville.senate.gov"
  },
  {
    "name": "Katie Boyd Britt",
    "state": "Alabama",
    "website": "https://www.britt.senate.gov"
  },
  {
    "name": "Lisa Murkowski",
    "state": "Alaska",
    "website": "https://www.murkowski.senate.gov"
  },
  {
    "name": "Dan Sullivan",
    "state": "Alaska",
    "website": "https://www.sullivan.senate.gov"
  },
  {
    "name": "Mark Kelly",
    "state": "Arizona",
    "website": "https://www.kelly.senate.gov"
  },
  {
    "name": "Kyrsten Sinema",
    "state": "Arizona",
    "website": "https://www.sinema.senate.gov"
  },
  {
    "name": "John Boozman",
    "state": "Arkansas",
    "website": "https://www.boozman.senate.gov"
  },
  {
    "name": "Tom Cotton",
    "state": "Arkansas",
    "website": "https://www.cotton.senate.gov"
  },
  {
    "name": "Alex Padilla",
    "state": "California",
    "website": "https://www.padilla.senate.gov"
  },
  {
    "name": "Laphonza Butler",
    "state": "California",
    "website": "https://www.butler.senate.gov"
  },
  {
    "name": "Michael Bennet",
    "state": "Colorado",
    "website": "https://www.bennet.senate.gov"
  },
  {
    "name": "John Hickenlooper",
    "state": "Colorado",
    "website": "https://www.hickenlooper.senate.gov"
  },
  {
    "name": "Richard Blumenthal",
    "state": "Connecticut",
    "website": "https://www.blumenthal.senate.gov"
  },
  {
    "name": "Chris Murphy",
    "state": "Connecticut",
    "website": "https://www.murphy.senate.gov"
  },
  {
    "name": "Tom Carper",
    "state": "Delaware",
    "website": "https://www.carper.senate.gov"
  },
  {
    "name": "Chris Coons",
    "state": "Delaware",
    "website": "https://www.coons.senate.gov"
  },
  {
    "name": "Marco Rubio",
    "state": "Florida",
    "website": "https://www.rubio.senate.gov"
  },
  {
    "name": "Rick Scott",
    "state": "Florida",
    "website": "https://www.rickscott.senate.gov"
  },
  {
    "name": "Jon Ossoff",
    "state": "Georgia",
    "website": "https://www.ossoff.senate.gov"
  },
  {
    "name": "Raphael Warnock",
    "state": "Georgia",
    "website": "https://www.warnock.senate.gov"
  },
  {
    "name": "Brian Schatz",
    "state": "Hawaii",
    "website": "https://www.schatz.senate.gov"
  },
  {
    "name": "Mazie Hirono",
    "state": "Hawaii",
    "website": "https://www.hirono.senate.gov"
  },
  {
    "name": "Mike Crapo",
    "state": "Idaho",
    "website": "https://www.crapo.senate.gov"
  },
  {
    "name": "Jim Risch",
    "state": "Idaho",
    "website": "https://www.risch.senate.gov"
  },
  {
    "name": "Dick Durbin",
    "state": "Illinois",
    "website": "https://www.durbin.senate.gov"
  },
  {
    "name": "Tammy Duckworth",
    "state": "Illinois",
    "website": "https://www.duckworth.senate.gov"
  },
  {
    "name": "Todd Young",
    "state": "Indiana",
    "website": "https://www.young.senate.gov"
  },
  {
    "name": "Mike Braun",
    "state": "Indiana",
    "website": "https://www.braun.senate.gov"
  },
  {
    "name": "Chuck Grassley",
    "state": "Iowa",
    "website": "https://www.grassley.senate.gov"
  },
  {
    "name": "Joni Ernst",
    "state": "Iowa",
    "website": "https://www.ernst.senate.gov"
  },
  {
    "name": "Jerry Moran",
    "state": "Kansas",
    "website": "https://www.moran.senate.gov"
  },
  {
    "name": "Roger Marshall",
    "state": "Kansas",
    "website": "https://www.marshall.senate.gov"
  },
  {
    "name": "Mitch McConnell",
    "state": "Kentucky",
    "website": "https://www.mcconnell.senate.gov"
  },
  {
    "name": "Rand Paul",
    "state": "Kentucky",
    "website": "https://www.paul.senate.gov"
  },
  {
    "name": "Bill Cassidy",
    "state": "Louisiana",
    "website": "https://www.cassidy.senate.gov"
  },
  {
    "name": "John Kennedy",
    "state": "Louisiana",
    "website": "https://www.kennedy.senate.gov"
  },
  {
    "name": "Susan Collins",
    "state": "Maine",
    "website": "https://www.collins.senate.gov"
  },
  {
    "name": "Angus King",
    "state": "Maine",
    "website": "https://www.king.senate.gov"
  },
  {
    "name": "Ben Cardin",
    "state": "Maryland",
    "website": "https://www.cardin.senate.gov"
  },
  {
    "name": "Chris Van Hollen",
    "state": "Maryland",
    "website": "https://www.vanhollen.senate.gov"
  },
  {
    "name": "Elizabeth Warren",
    "state": "Massachusetts",
    "website": "https://www.warren.senate.gov"
  },
  {
    "name": "Ed Markey",
    "state": "Massachusetts",
    "website": "https://www.markey.senate.gov"
  },
  {
    "name": "Debbie Stabenow",
    "state": "Michigan",
    "website": "https://www.stabenow.senate.gov"
  },
  {
    "name": "Gary Peters",
    "state": "Michigan",
    "website": "https://www.peters.senate.gov"
  },
  {
    "name": "Amy Klobuchar",
    "state": "Minnesota",
    "website": "https://www.klobuchar.senate.gov"
  },
  {
    "name": "Tina Smith",
    "state": "Minnesota",
    "website": "https://www.smith.senate.gov"
  },
  {
    "name": "Roger Wicker",
    "state": "Mississippi",
    "website": "https://www.wicker.senate.gov"
  },
  {
    "name": "Cindy Hyde-Smith",
    "state": "Mississippi",
    "website": "https://www.hydesmith.senate.gov"
  },
  {
    "name": "Josh Hawley",
    "state": "Missouri",
    "website": "https://www.hawley.senate.gov"
  },
  {
    "name": "Eric Schmitt",
    "state": "Missouri",
    "website": "https://www.schmitt.senate.gov"
  },
  {
    "name": "Jon Tester",
    "state": "Montana",
    "website": "https://www.tester.senate.gov"
  },
  {
    "name": "Steve Daines",
    "state": "Montana",
    "website": "https://www.daines.senate.gov"
  },
  {
    "name": "Deb Fischer",
    "state": "Nebraska",
    "website": "https://www.fischer.senate.gov"
  },
  {
    "name": "Pete Ricketts",
    "state": "Nebraska",
    "website": "https://www.ricketts.senate.gov"
  },
  {
    "name": "Jacky Rosen",
    "state": "Nevada",
    "website": "https://www.rosen.senate.gov"
  },
  {
    "name": "Catherine Cortez Masto",
    "state": "Nevada",
    "website": "https://www.cortezmasto.senate.gov"
  },
  {
    "name": "Jeanne Shaheen",
    "state": "New Hampshire",
    "website": "https://www.shaheen.senate.gov"
  },
  {
    "name": "Maggie Hassan",
    "state": "New Hampshire",
    "website": "https://www.hassan.senate.gov"
  },
  {
    "name": "Bob Menendez",
    "state": "New Jersey",
    "website": "https://www.menendez.senate.gov"
  },
  {
    "name": "Cory Booker",
    "state": "New Jersey",
    "website": "https://www.booker.senate.gov"
  },
  {
    "name": "Martin Heinrich",
    "state": "New Mexico",
    "website": "https://www.heinrich.senate.gov"
  },
  {
    "name": "Ben Ray Luján",
    "state": "New Mexico",
    "website": "https://www.lujan.senate.gov"
  },
  {
    "name": "Chuck Schumer",
    "state": "New York",
    "website": "https://www.schumer.senate.gov"
  },
  {
    "name": "Kirsten Gillibrand",
    "state": "New York",
    "website": "https://www.gillibrand.senate.gov"
  },
  {
    "name": "Ted Budd",
    "state": "North Carolina",
    "website": "https://www.budd.senate.gov"
  },
  {
    "name": "Thom Tillis",
    "state": "North Carolina",
    "website": "https://www.tillis.senate.gov"
  },
  {
    "name": "John Hoeven",
    "state": "North Dakota",
    "website": "https://www.hoeven.senate.gov"
  },
  {
    "name": "Kevin Cramer",
    "state": "North Dakota",
    "website": "https://www.cramer.senate.gov"
  },
  {
    "name": "Sherrod Brown",
    "state": "Ohio",
    "website": "https://www.brown.senate.gov"
  },
  {
    "name": "JD Vance",
    "state": "Ohio",
    "website": "https://www.vance.senate.gov"
  },
  {
    "name": "Markwayne Mullin",
    "state": "Oklahoma",
    "website": "https://www.mullin.senate.gov"
  },
  {
    "name": "James Lankford",
    "state": "Oklahoma",
    "website": "https://www.lankford.senate.gov"
  },
  {
    "name": "Ron Wyden",
    "state": "Oregon",
    "website": "https://www.wyden.senate.gov"
  },
  {
    "name": "Jeff Merkley",
    "state": "Oregon",
    "website": "https://www.merkley.senate.gov"
  },
  {
    "name": "Bob Casey",
    "state": "Pennsylvania",
    "website": "https://www.casey.senate.gov"
  },
  {
    "name": "John Fetterman",
    "state": "Pennsylvania",
    "website": "https://www.fetterman.senate.gov"
  },
  {
    "name": "Jack Reed",
    "state": "Rhode Island",
    "website": "https://www.reed.senate.gov"
  },
  {
    "name": "Sheldon Whitehouse",
    "state": "Rhode Island",
    "website": "https://www.whitehouse.senate.gov"
  },
  {
    "name": "Lindsey Graham",
    "state": "South Carolina",
    "website": "https://www.lgraham.senate.gov"
  },
  {
    "name": "Tim Scott",
    "state": "South Carolina",
    "website": "https://www.scott.senate.gov"
  },
  {
    "name": "John Thune",
    "state": "South Dakota",
    "website": "https://www.thune.senate.gov"
  },
  {
    "name": "Mike Rounds",
    "state": "South Dakota",
    "website": "https://www.rounds.senate.gov"
  },
  {
    "name": "Marsha Blackburn",
    "state": "Tennessee",
    "website": "https://www.blackburn.senate.gov"
  },
  {
    "name": "Bill Hagerty",
    "state": "Tennessee",
    "website": "https://www.hagerty.senate.gov"
  },
  {
    "name": "John Cornyn",
    "state": "Texas",
    "website": "https://www.cornyn.senate.gov"
  },
  {
    "name": "Ted Cruz",
    "state": "Texas",
    "website": "https://www.cruz.senate.gov"
  },
  {
    "name": "Mitt Romney",
    "state": "Utah",
    "website": "https://www.romney.senate.gov"
  },
  {
    "name": "Mike Lee",
    "state": "Utah",
    "website": "https://www.lee.senate.gov"
  },
  {
    "name": "Bernie Sanders",
    "state": "Vermont",
    "website": "https://www.sanders.senate.gov"
  },
  {
    "name": "Peter Welch",
    "state": "Vermont",
    "website": "https://www.welch.senate.gov"
  },
  {
    "name": "Mark Warner",
    "state": "Virginia",
    "website": "https://www.warner.senate.gov"
  },
  {
    "name": "Tim Kaine",
    "state": "Virginia",
    "website": "https://www.kaine.senate.gov"
  },
  {
    "name": "Patty Murray",
    "state": "Washington",
    "website": "https://www.murray.senate.gov"
  },
  {
    "name": "Maria Cantwell",
    "state": "Washington",
    "website": "https://www.cantwell.senate.gov"
  },
  {
    "name": "Joe Manchin",
    "state": "West Virginia",
    "website": "https://www.manchin.senate.gov"
  },
  {
    "name": "Shelley Moore Capito",
    "state": "West Virginia",
    "website": "https://www.capito.senate.gov"
  },
  {
    "name": "Tammy Baldwin",
    "state": "Wisconsin",
    "website": "https://www.baldwin.senate.gov"
  },
  {
    "name": "Ron Johnson",
    "state": "Wisconsin",
    "website": "https://www.ronjohnson.senate.gov"
  },
  {
    "name": "John Barrasso",
    "state": "Wyoming",
    "website": "https://www.barrasso.senate.gov"
  },
  {
    "name": "Cynthia Lummis",
    "state": "Wyoming",
    "website": "https://www.lummis.senate.gov"
  }
]

senators: List[Dict[str, Any]] = [
    {
        "congress_id": _generate_congress_id(sen["name"], sen["state"]),
        "image_filename": _generate_image_filename(sen["name"]),
        **sen
    }
    for sen in senators_raw
]

# del representatives_raw # Optional cleanup
# del senators_raw

# --- Helper functions for Static Data --- #
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

    for rep in representatives:
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
    return [sen for sen in senators if sen['state'].lower() == normalized_state.lower()]

def find_member_by_id(congress_id: str):
    """Finds any member (rep or senator) by congress_id from static data."""
    for rep in representatives:
        if rep['congress_id'] == congress_id:
            return rep
    for sen in senators:
        if sen['congress_id'] == congress_id:
            return sen
    return None 