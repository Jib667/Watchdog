#!/bin/bash

# Setup Script for Watchdog Backend
echo "====== Watchdog Backend Setup ======"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv ../venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source ../venv/bin/activate || { echo "Error: Failed to activate virtual environment."; exit 1; }

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt || { echo "Error: Failed to install dependencies."; exit 1; }

# Create necessary directories
echo "Setting up directory structure..."
mkdir -p ../backend/data

# Initialize the database
echo "Initializing database..."
python init_db.py || { echo "Error: Failed to initialize database."; exit 1; }

echo
echo "====== Setup complete! ======"
echo "To start the server, run: python server.py"
echo "The API will be available at: http://localhost:5000"
echo
echo "API documentation will be available at:"
echo "- http://localhost:5000/docs (Swagger UI)"
echo "- http://localhost:5000/redoc (ReDoc)"
echo 