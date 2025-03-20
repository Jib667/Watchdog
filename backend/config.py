import os
from dotenv import load_dotenv

# Load environment variables from .env file in the root directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

# Congress API Configuration
CONGRESS_API_KEY = os.getenv("CONGRESS_API_KEY", "")
CONGRESS_API_URL = os.getenv("CONGRESS_API_URL", "https://api.congress.gov/v3")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./watchdog.db")

# Server Configuration
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("NODE_ENV", "development") == "development"

def get_api_config():
    """
    Get the Congress API configuration as a dictionary.
    
    Returns:
        dict: API configuration with api_key and base_url
    """
    return {
        "api_key": CONGRESS_API_KEY,
        "base_url": CONGRESS_API_URL
    }

def is_api_configured():
    """
    Check if the Congress API is properly configured.
    
    Returns:
        bool: True if API key is present, False otherwise
    """
    return bool(CONGRESS_API_KEY) 