# Watchdog Backend

This is the backend component of the Watchdog application for monitoring congressional representatives and their voting records.

## Project Structure

The backend is structured as follows:

- `server.py`: Main application entry point with FastAPI routes
- `database.py`: Database models, schema definitions, and connection management
- `data_manager.py`: Utilities for importing and managing data
- `congress_api.py`: Integration with the Congress API for real-time data
- `requirements.txt`: Python dependencies

## Setup Instructions

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the Congress API (optional but recommended):
   Set your API key in the environment variables:
   ```bash
   export CONGRESS_API_KEY="your_api_key_here"
   ```
   
   Or configure it through the API after starting the server (see API Configuration section below)

4. Start the server:
   ```bash
   python server.py
   ```

   The server will run on http://localhost:5000

## Database Management

The application uses SQLite by default, stored in `watchdog.db`.

### Database Models

- `User`: Registered users of the application
- `Representative`: Members of the House and Senate
- `Bill`: Congressional bills and their statuses
- `Vote`: Voting records linking representatives to bills
- `ApiConfig`: Configuration for external APIs like the Congress API

### Working with Data

The `data_manager.py` file provides utilities for data management:

#### Generating Sample Data

For development purposes, you can generate sample data:

```bash
python data_manager.py
```

This will create sample representatives, bills, and voting records.

#### Importing Data

The data manager supports importing data from CSV and JSON files:

- Import representatives:
  ```bash
  python -c "from data_manager import import_representatives_from_csv; import_representatives_from_csv('path/to/representatives.csv')"
  ```

- Import bills:
  ```bash
  python -c "from data_manager import import_bills_from_json; import_bills_from_json('path/to/bills.json')"
  ```

- Import votes:
  ```bash
  python -c "from data_manager import import_votes_from_csv; import_votes_from_csv('path/to/votes.csv')"
  ```

#### Resetting the Database

To reset the database (caution: this will delete all data):

```bash
python -c "from data_manager import reset_database; reset_database()"
```

## Congress API Integration

The application integrates with the [Congress API](https://api.congress.gov/) to fetch real-time data about representatives, bills, and voting records.

### API Configuration

You can configure the Congress API in two ways:

1. Through environment variables:
   ```bash
   export CONGRESS_API_KEY="your_api_key_here"
   export CONGRESS_API_URL="https://api.congress.gov/v3"  # Optional, default value
   ```

2. Through the API (after starting the server):
   ```bash
   curl -X POST "http://localhost:5000/api/config" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "congress_api",
       "api_key": "your_api_key_here",
       "base_url": "https://api.congress.gov/v3",
       "is_active": true
     }'
   ```

### Data Synchronization

The application provides endpoints to synchronize data from the Congress API:

- Sync representatives:
  ```bash
  curl -X POST "http://localhost:5000/api/sync/representatives"
  ```

- Sync recent bills (last 30 days by default):
  ```bash
  curl -X POST "http://localhost:5000/api/sync/bills?days_back=30"
  ```

- Sync votes for a specific representative:
  ```bash
  curl -X POST "http://localhost:5000/api/sync/representatives/1/votes"
  ```

### Testing the API Connection

You can test the connection to the Congress API:

```bash
curl "http://localhost:5000/api/test/congress-api"
```

## API Documentation

### Congress API Integration

This application integrates with the Congress.gov API to fetch and synchronize data about congressional activities. The API provides information about:

- Representatives (House and Senate members)
- Bills and their status
- Voting records

### Setting Up API Access

1. **API Key**: You need an API key from Congress.gov. Set it in the `.env` file as `CONGRESS_API_KEY`.
2. **Verify Configuration**: Check the API configuration status using the `/api/config/api` endpoint.
3. **Update Configuration**: You can update the API configuration using the same endpoint with a POST request.

### Data Synchronization

The application provides endpoints to synchronize data from the Congress API:

- `/api/sync/status` - Get current synchronization status
- `/api/sync/representatives` - Sync representatives data
- `/api/sync/bills` - Sync bills data
- `/api/sync/votes` - Sync votes data
- `/api/sync/all` - Sync all data

Synchronization can run in the background and supports force updating regardless of last update times.

### Available Endpoints

When the server is running, you can access the automatically generated API documentation at:

- http://localhost:5000/docs (Swagger UI)
- http://localhost:5000/redoc (ReDoc)

## Available Endpoints

### Users

- `GET /users/`: List all users
- `POST /users/`: Create a new user
- `GET /users/{user_id}`: Get a specific user
- `DELETE /users/{user_id}`: Delete a user

### Representatives

- `GET /representatives/`: List representatives (with optional filters)
- `GET /representatives/{rep_id}`: Get a specific representative
- `GET /representatives/{rep_id}/votes`: Get a representative's voting record

### Bills

- `GET /bills/`: List bills (with optional filters)
- `GET /bills/{bill_id}`: Get a specific bill
- `GET /bills/{bill_id}/votes`: Get voting records for a specific bill

### Votes

- `GET /votes/`: List votes (with optional filters)

### Congress API Integration

- `GET /api/config`: List all API configurations
- `GET /api/config/{name}`: Get a specific API configuration
- `POST /api/config`: Create or update an API configuration
- `POST /api/sync/representatives`: Sync representatives from the Congress API
- `POST /api/sync/bills`: Sync recent bills from the Congress API
- `POST /api/sync/representatives/{rep_id}/votes`: Sync votes for a specific representative
- `GET /api/test/congress-api`: Test the connection to the Congress API

## Environment Variables

You can configure the application using environment variables:

- `DATABASE_URL`: Database connection string (default: `sqlite:///./watchdog.db`)
- `CONGRESS_API_KEY`: API key for the Congress API
- `CONGRESS_API_URL`: Base URL for the Congress API (default: `https://api.congress.gov/v3`)

## Development

The codebase follows modern Python practices with type hints and documentation for better maintainability. 