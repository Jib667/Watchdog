# Watchdog - Congressional Monitoring Platform

Watchdog is a web application designed to provide citizens with accessible information about the U.S. Congress. It allows users to explore data on current members of the House and Senate, their committee assignments, and basic biographical information.

## Project Structure

*   `backend/`: Contains the FastAPI backend application.
    *   `app/`: Core application logic, including API routes, data loading, and models.
        *   `main.py`: Main FastAPI application entry point (or adjust if different).
        *   `core.py`: Handles loading and processing data from local static files.
        *   `api.py`: Defines the API endpoints.
        *   `static/congress_data/`: Stores the downloaded legislator/committee YAML data files and the processed bill/vote data copied from the congress tools.
            *   `*.yaml`: Legislator, Committee, Membership YAML files.
            *   `congress/<congress_num>/`: Contains processed Bill and Vote data (JSON/XML).
    *   `update_congress_members_data.py`: Script to download the latest legislator/committee YAML data files.
    *   `update_bill_vote_data.py`: Script to manage the `congress_tools` and generate/copy bill/vote data.
    *   `requirements.txt`: Python dependencies for the backend.
    *   `.env` / `.env.example`: Environment variable configuration (if used).
*   `frontend/`: Contains the React frontend application built with Vite.
*   `congress_tools/`: **(Local Only - Not Committed)** Directory created locally when `update_bill_vote_data.py` is run. Contains a clone of the `unitedstates/congress` repository and its tools/dependencies. Ignored by Git.
    *   `src/`: Frontend source code (components, pages, styles).
    *   `package.json`: Node.js dependencies and scripts.
*   `README.md`: This file.
*   `.gitignore`: Specifies intentionally untracked files that Git should ignore.

## Data Source

The primary source for congressional member and committee data is the open-source `unitedstates/congress-legislators` repository:
[https://github.com/unitedstates/congress-legislators](https://github.com/unitedstates/congress-legislators)

The source for bill and vote data collection tools is the `unitedstates/congress` repository:
[https://github.com/unitedstates/congress](https://github.com/unitedstates/congress)

## Getting Started

### Prerequisites

*   Python 3.9 or higher
*   Node.js 16 or higher (comes with npm)
*   `pip` (Python package installer)
*   `npm` (Node package manager)
*   **System Dependencies (for Bill/Vote data generation):** `git`, `wget`, and potentially development libraries like `libxml2-dev`, `libxslt1-dev`, `zlib1g-dev` (Linux) or Xcode Command Line Tools (macOS). See setup notes below.

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    # Run from project root
    cd backend
    ```

2.  **(Required for Bill/Vote Data Script) Install System Dependencies:**
    The `update_bill_vote_data.py` script relies on tools from the `unitedstates/congress` repository, which requires certain system-level tools.
    *   **On macOS (using Homebrew):**
        ```bash
        # Ensure Xcode Command Line Tools are installed (provides libraries like libxml2, etc.)
        xcode-select --install
        # Install required tools if not already present
        brew install git wget python3
        ```
    *   **On Debian/Ubuntu Linux:**
        ```bash
        sudo apt-get update && sudo apt-get install git python3 python3-pip python3-venv wget libxml2-dev libxslt1-dev zlib1g-dev -y
        ```
    *You only need to do this system setup once.*

3.  **Create and activate a Python virtual environment (Recommended):**
    ```bash
    # Create the virtual environment
    python3 -m venv venv
    # Activate it (macOS/Linux)
    source venv/bin/activate
    # Or (Windows - Command Prompt/PowerShell)
    # .\venv\Scripts\activate
    ```

4.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(This includes the `requests` library needed for the member update script.)*

5.  **Download/Generate Initial Congressional Data:**
    Run the two update scripts. **Note:** `update_bill_vote_data.py` can take a very long time on its first run as it processes historical data.
    ```bash
    python update_congress_members_data.py # Fetches legislator/committee YAMLs
    python update_bill_vote_data.py      # Clones tools, generates & copies bill/vote data
    ```
    *(These scripts populate `backend/app/static/congress_data/` and create the local `congress_tools/` directory respectively.)*

6.  **Configure Environment (If applicable):**
    If your project uses a `.env` file for configuration (e.g., for secrets or API keys if added later), copy `.env.example` to `.env` and fill in the required values.

7.  **Start the backend server:**
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

To update the local data files:

1.  Navigate to the `backend` directory.
2.  Ensure your Python virtual environment is active (`source venv/bin/activate` or equivalent).
3.  Run the desired update script(s):
    ```bash
    python update_congress_members_data.py # Update legislator/committee YAMLs (quick)
    python update_bill_vote_data.py      # Update bills/votes for recent Congress (can be slow)
    ```
    *Note: The `update_bill_vote_data.py` script manages the `congress_tools/` directory locally and copies the generated data to `backend/app/static/congress_data/congress/`. Remember to commit changes to the copied data in `backend/app/static/congress_data/congress/` if you want to include updated bill/vote data in the repository.*

4.  Restart the backend server (Uvicorn with `--reload` should restart automatically, but a manual restart ensures the new data is loaded if `--reload` isn't used or fails).

## API Documentation

Once the backend server is running, interactive API documentation (provided by FastAPI) is usually available at:

*   Swagger UI: `http://localhost:8000/docs`
*   ReDoc: `http://localhost:8000/redoc`

## Technology Stack

*   **Backend**: FastAPI (Python), Uvicorn, PyYAML
*   **Frontend**: React, Vite, React Router, React Bootstrap
*   **Data Source**: YAML files from `unitedstates/congress-legislators`
*   **Data Generation Tools (Local)**: `unitedstates/congress` tools (run locally via script)

## License

*   **Project Code**: [Specify your chosen license here, e.g., MIT License] - see the LICENSE file for details.
*   **Congressional Data**: The data from `unitedstates/congress-legislators` is dedicated to the public domain via CC0 1.0 Universal. 