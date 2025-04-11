#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Watchdog project...${NC}"

# --- Backend Setup --- 
echo -e "\n${YELLOW}--- Setting up Backend ---${NC}"

# Navigate to backend
cd backend || { echo -e "${RED}Error: Could not change directory to backend.${NC}"; exit 1; }

# Create necessary directories
echo -e "${YELLOW}Creating backend directories (./data, ./app/static/congress_data)...${NC}"
mkdir -p ./data
mkdir -p ./app/static/congress_data # Ensure data directory exists before download

# Create backend .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating backend .env file...${NC}"
    cat > .env << EOL
# Database configuration (adjust if needed)
DATABASE_URL=sqlite:///./data/watchdog.db

# JWT configuration (auto-generated)
JWT_SECRET=$(openssl rand -hex 32)

# Default Admin user configuration (CHANGE THESE!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=watchdog123
EOL
    echo -e "${GREEN}Created .env file. Please review and change default ADMIN_PASSWORD.${NC}"
else
    echo -e "${YELLOW}Backend .env file already exists, skipping creation.${NC}"
fi

# Set up Python virtual environment
echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
python3 -m venv venv || { echo -e "${RED}Error: Failed to create virtual environment.${NC}"; exit 1; }

# Activate virtual environment (temporarily for this script)
source venv/bin/activate || { echo -e "${RED}Error: Failed to activate virtual environment.${NC}"; exit 1; }

# Install backend dependencies
echo -e "${YELLOW}Installing backend dependencies from requirements.txt...${NC}"
pip install -r requirements.txt || { echo -e "${RED}Error: Failed to install backend requirements.${NC}"; deactivate; exit 1; }

# Download initial congressional data
echo -e "${YELLOW}Downloading initial congressional data...${NC}"
python update_congress_members_data.py || { echo -e "${RED}Error: Failed to download congressional data.${NC}"; deactivate; exit 1; }

# Deactivate venv for now (user will activate manually later)
deactivate

# Navigate back to root
cd .. || { echo -e "${RED}Error: Could not change back to root directory.${NC}"; exit 1; }

# --- Frontend Setup --- 
echo -e "\n${YELLOW}--- Setting up Frontend ---${NC}"

# Navigate to frontend
cd frontend || { echo -e "${RED}Error: Could not change directory to frontend.${NC}"; exit 1; }

# Install frontend dependencies
echo -e "${YELLOW}Installing frontend dependencies with npm...${NC}"
npm install || { echo -e "${RED}Error: Failed to install frontend dependencies.${NC}"; exit 1; }

# Navigate back to root
cd .. || { echo -e "${RED}Error: Could not change back to root directory.${NC}"; exit 1; }


echo -e "\n${GREEN}--- Setup Completed Successfully! ---${NC}"
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. Review and potentially modify ${GREEN}backend/.env${NC} (especially the default ADMIN_PASSWORD)."
echo -e "2. Review and potentially modify ${GREEN}frontend/.env${NC} (especially VITE_API_URL if not using defaults)."
echo -e "3. To start the backend server:
   ${GREEN}cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000${NC}"
echo -e "4. To start the frontend development server (in a separate terminal):
   ${GREEN}cd frontend && npm run dev${NC}" 