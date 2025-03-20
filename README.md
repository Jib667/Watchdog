# Watchdog

A web application for monitoring representatives and senators of Congress

## Features

- View platforms of representatives and senators easily
- View voting records of representatives and senators
- See contradictions and view past actions
- Contact your representatives directly

## Project Structure

- `frontend/`: React-based frontend application with Vite
  - Components for each page (Home, Representatives, Senate, Contact)
  - Sidebar navigation component
  - CSS styling for all components
- `backend/`: Python FastAPI backend with SQLite database
  - User registration API
  - Data retrieval endpoints for congressional information

## Pages

- **Home**: Landing page with website information
- **House of Representatives**: Map and viewing system for members of the House of Representatives
- **Senate**: Map and viewing system for members of the Senate
- **Contact**: Contact the representative or senator of your choice

## Setup Instructions

### Backend Setup

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
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   python server.py
   ```
   
   The server will run on http://localhost:5000

### Frontend Setup

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

## API Documentation

When the backend server is running, you can access the automatically generated API documentation at:
- http://localhost:5000/docs (Swagger UI)
- http://localhost:5000/redoc (ReDoc)

## Technologies Used

- Frontend:
  - React.js
  - React Router
  - Vite
  - CSS3
- Backend:
  - Python 3.8+
  - FastAPI
  - SQLAlchemy
  - SQLite
  - Uvicorn

## Future Enhancements

- Implement interactive US maps for state selection
- Add real-time data from Congress API
- Add authentication for personalized experience
- Add more detailed profiles for representatives and senators
- Implement voting record comparison tools 