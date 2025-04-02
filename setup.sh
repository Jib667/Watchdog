#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Watchdog project...${NC}"

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p backend/data
mkdir -p frontend/public/images

# Create backend .env file
echo -e "${YELLOW}Creating backend .env file...${NC}"
cat > backend/.env << EOL
# Database configuration
DATABASE_URL=sqlite:///data/watchdog.db

# JWT configuration
JWT_SECRET=$(openssl rand -hex 32)

# Admin user configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=watchdog123
EOL

# Create root .env file
echo -e "${YELLOW}Creating root .env file...${NC}"
cat > .env << EOL
# Database configuration
DATABASE_URL=sqlite:///data/watchdog.db

# JWT configuration
JWT_SECRET=$(openssl rand -hex 32)

# Admin user configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=watchdog123
EOL

# Install backend dependencies
echo -e "${YELLOW}Installing backend dependencies...${NC}"
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
cd backend
source venv/bin/activate
python init_db.py
cd ..

echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${YELLOW}To start the backend server:${NC}"
echo -e "cd backend && source venv/bin/activate && python server.py"
echo -e "${YELLOW}To start the frontend development server:${NC}"
echo -e "cd frontend && npm run dev" 