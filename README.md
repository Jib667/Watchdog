# Watchdog

A web application for monitoring representatives and senators of Congress

## Features

- View platforms of representatives and senators easily
- View voting records of representatives and senators
- See contradictions and view past actions

## Project Structure

- `frontend/`: React-based frontend application with Vite
- `backend/`: Python FastAPI backend with SQLite database

## Pages

- **Home**: Landing page with website information
- **House of Representatives**: Map and viewing system for members of the House of Representatives
- **Senate**: Map and viewing system for members of the Senate
- **Contact**: Contact the representative or senator of your choice

### Manual Setup from GutHub

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install uv
   uv pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   python server.py
   ```
   
   The server will run on http://localhost:5000

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the frontend development server:
   ```bash
   npm run dev
   ```
   
   The application will be available at http://localhost:5173

### Important Note

Both the frontend and backend servers need to be running simultaneously for the application to work properly. The frontend Vite server is configured to proxy API requests to the backend server.

## Sign-Up Functionality

The application includes a sign-up form that collects:
- Full name
- Email address

This information is stored in an SQLite database on the backend.

## API Documentation

When the backend server is running, you can access the automatically generated API documentation at:
- http://localhost:5000/docs (Swagger UI)
- http://localhost:5000/redoc (ReDoc)

## Technologies Used

- React.js
- Vite
- Python 3.8+
- FastAPI
- SQLite
- UV (Python package installer) 