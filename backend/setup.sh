#!/bin/bash
# Watchdog Backend Setup Script
# This script sets up the Watchdog backend environment

# Exit on any error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}  Setting up Watchdog Backend      ${NC}"
echo -e "${GREEN}====================================${NC}"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate || source venv/Scripts/activate

# Install requirements
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Generate a JWT secret key
JWT_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    echo "# Watchdog Backend Environment Variables" > .env
    echo "CONGRESS_API_KEY=" >> .env
    echo "CONGRESS_API_URL=https://api.congress.gov/v3" >> .env
    echo "DATABASE_URL=sqlite:///./watchdog.db" >> .env
    echo "JWT_SECRET=${JWT_SECRET}" >> .env
    echo "ADMIN_USERNAME=admin" >> .env
    echo "ADMIN_PASSWORD=watchdog123" >> .env
    echo -e "${YELLOW}Created .env file. Please edit it to add your Congress.gov API key.${NC}"
    echo -e "${YELLOW}You can get an API key from https://api.congress.gov/sign-up${NC}"
    echo -e "${YELLOW}Also, please change the default admin password in the .env file!${NC}"
fi

# Reset and initialize the database
echo -e "${YELLOW}Initializing database...${NC}"
python fix_database.py
python init_db.py

echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}  Setup completed successfully!     ${NC}"
echo -e "${GREEN}====================================${NC}"
echo -e "${YELLOW}To start the server, run:${NC}"
echo -e "${GREEN}source venv/bin/activate${NC}"
echo -e "${GREEN}python -m uvicorn server:app --reload${NC}"
echo -e "${YELLOW}The API will be available at:${NC}"
echo -e "${GREEN}http://localhost:8000${NC}"
echo -e "${YELLOW}API documentation:${NC}"
echo -e "${GREEN}http://localhost:8000/docs${NC}"
echo -e "${YELLOW}Default admin credentials:${NC}"
echo -e "${GREEN}Username: admin${NC}"
echo -e "${GREEN}Password: watchdog123${NC}" 