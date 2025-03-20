# Watchdog - Congressional Monitoring Platform

Watchdog is a web application that allows users to monitor congressional activity, including bills, votes, and representatives. All congressional data is fetched directly from the Congress.gov API in real-time, ensuring the most up-to-date information.

## Project Structure

### Backend

The backend is a FastAPI application that connects to the Congress.gov API and provides a user authentication system. Users can create accounts, save favorite representatives and bills, and access real-time congressional data.

- `server.py` - Main FastAPI application with API endpoints
- `fix_database.py` - Utility to reset the database
- `init_db.py` - Database initialization script
- `setup.sh` - Setup script for the backend environment
- `requirements.txt` - Python dependencies

### Frontend

The frontend is a React application built with Vite, providing a user interface for interacting with the congressional data.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- npm 7 or higher
- A Congress.gov API key (get one from [https://api.congress.gov/sign-up](https://api.congress.gov/sign-up))

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Run the setup script:
   ```
   bash setup.sh
   ```

3. Edit the `.env` file to add your Congress.gov API key and change the default admin password:
   ```
   CONGRESS_API_KEY=your_api_key_here
   ADMIN_PASSWORD=your_secure_password
   ```

4. Start the backend server:
   ```
   source venv/bin/activate
   python -m uvicorn server:app --reload
   ```

The API will be accessible at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

The frontend will be accessible at http://localhost:5173

## API Documentation

Once the backend server is running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Features

- **User Authentication**: Create accounts, login, and save personalized preferences
- **Representatives Monitoring**: View information about current members of Congress, including representatives and senators
- **Bill Tracking**: Monitor recently introduced bills and their status
- **Vote Records**: Track recent votes in the House and Senate
- **Favorites**: Save representatives and bills to your personal watchlist

## Backend API Endpoints

### Public Endpoints
- `/api/representatives` - Get all representatives
- `/api/representatives/house` - Get House representatives
- `/api/representatives/senate` - Get Senate representatives
- `/api/bills/recent` - Get recent bills
- `/api/votes/recent` - Get recent votes

### Authentication Endpoints
- `/api/auth/register` - Register a new user
- `/api/auth/token` - Login and get an access token

### User Endpoints (requires authentication)
- `/api/users/me` - Get current user information
- `/api/users/me/representatives` - Get saved representatives
- `/api/users/me/bills` - Get saved bills
- `/api/users/me/representatives/{congress_id}` - Save/unsave a representative
- `/api/users/me/bills/{bill_id}` - Save/unsave a bill

### Admin Endpoints
- `/api/config/api` - Set/get API configuration

## Data Management

Unlike traditional applications that store and synchronize data with external APIs, Watchdog takes a different approach:

- **User data** (accounts, preferences, saved items) is stored in the local database
- **Congressional data** (representatives, bills, votes) is fetched directly from the Congress.gov API in real-time
- This approach ensures the most current information while simplifying the backend architecture

## Technology Stack

- **Backend**: FastAPI, SQLite, JWT Authentication
- **Frontend**: React, React Router, Vite
- **API**: Congress.gov API

## License

This project is licensed under the MIT License - see the LICENSE file for details. 