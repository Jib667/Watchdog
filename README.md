# Watchdog - Congressional Monitoring Platform

Watchdog is a web application designed to provide citizens with accessible information about the U.S. Congress. It allows users to explore data on current members of the House and Senate, their committee assignments, their previous votes, their campaign promises, basic biographical information, and whether or not they are voting along lines that match their proported platforms. 

## Project Structure

*   `backend/`: Contains the FastAPI backend application.
    *   `app/`: Core application logic, including API routes, data loading, and models.
        *   `main.py`: Main FastAPI application entry point (or adjust if different).
        *   `core.py`: Handles loading and processing data from YAML files.
        *   `api.py`: Defines the API endpoints.
        *   `static/congress_data/`: Stores the downloaded YAML data files.
    *   `update_congress_members_data.py`: Script to download the latest congressional data YAML files.
    *   `requirements.txt`: Python dependencies for the backend.
    *   `.env` / `.env.example`: Environment variable configuration (if used).
*   `frontend/`: Contains the React frontend application built with Vite.
    *   `src/`: Frontend source code (components, pages, styles).
    *   `package.json`: Node.js dependencies and scripts.
*   `README.md`: This file.
*   `.gitignore`: Specifies intentionally untracked files that Git should ignore.

## Data Source

The primary source for congressional member and committee data is the open-source `unitedstates/congress-legislators` repository:
[https://github.com/unitedstates/congress-legislators](https://github.com/unitedstates/congress-legislators)

This project provides structured data maintained by various contributors. Our application downloads specific YAML files from this repository to populate its local data store.

## Getting Started

### Prerequisites

*   Python 3.9 or higher
*   Node.js 16 or higher (comes with npm)
*   `pip` (Python package installer)
*   `npm` (Node package manager)

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a Python virtual environment (Recommended):**
    ```bash
    # Create the virtual environment
    python3 -m venv venv
    # Activate it (macOS/Linux)
    source venv/bin/activate
    # Or (Windows - Command Prompt/PowerShell)
    # .\venv\Scripts\activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(This includes the `requests` library needed for the update script.)*

4.  **Download Initial Congressional Data:**
    Run the update script to fetch the necessary YAML files:
    ```bash
    python update_congress_members_data.py
    ```
    *(This will populate the `backend/app/static/congress_data/` directory.)*

5.  **Configure Environment (If applicable):**
    If your project uses a `.env` file for configuration (e.g., for secrets or API keys if added later), copy `.env.example` to `.env` and fill in the required values.

6.  **Start the backend server:**
    ```bash
    # Make sure your virtual environment is active
    # Adjust 'app.main:app' if your FastAPI app instance is defined elsewhere
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The API should now be running, typically at `http://localhost:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory (from the project root):**
    ```bash
    cd frontend
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Configure Frontend Environment (If applicable):**
    The frontend might use environment variables (e.g., `VITE_API_URL` in `.env` within the `frontend` directory) to know where the backend API is located. Ensure this is set correctly (e.g., `VITE_API_URL=http://localhost:8000`). Check for a `.env.example` file in the frontend directory.

4.  **Start the frontend development server:**
    ```bash
    npm run dev
    ```
    The frontend application should now be accessible in your browser, typically at `http://localhost:5173` (Vite often uses port 5173 by default).

## Updating Congressional Data

To update the local YAML files with the latest data from the `congress-legislators` repository:

1.  Navigate to the `backend` directory.
2.  Ensure your Python virtual environment is active (`source venv/bin/activate` or equivalent).
3.  Run the update script:
    ```bash
    python update_congress_members_data.py
    ```
4.  Restart the backend server (Uvicorn with `--reload` should restart automatically, but a manual restart ensures the new data is loaded if `--reload` isn't used or fails).

## API Documentation

Once the backend server is running, interactive API documentation (provided by FastAPI) is usually available at:

*   Swagger UI: `http://localhost:8000/docs`
*   ReDoc: `http://localhost:8000/redoc`

## Technology Stack

*   **Backend**: FastAPI (Python), Uvicorn, PyYAML
*   **Frontend**: React, Vite, React Router, React Bootstrap
*   **Data Source**: YAML files from `unitedstates/congress-legislators`

## License

*   **Project Code**: [Specify your chosen license here, e.g., MIT License] - see the LICENSE file for details.
*   **Congressional Data**: The data from `unitedstates/congress-legislators` is dedicated to the public domain via CC0 1.0 Universal. 