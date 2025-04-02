"""
Main FastAPI application for the Watchdog backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import from consolidated modules
from .api import router as api_router # Import the single router
from .db import init_db
from .core import APP_DIR # Import APP_DIR to locate static files

app = FastAPI(
    title="Watchdog API",
    description="API for the Watchdog congressional monitoring platform",
    version="1.0.0"
)

# Mount static files directory (for images)
# This needs to be defined relative to where the app runs (likely backend/)
# or use an absolute path based on core.APP_DIR
static_dir = APP_DIR / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the consolidated API router
app.include_router(api_router, prefix="/api") # Include the single router

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    print("Initializing database...")
    try:
        init_db() # Call init_db from the consolidated db module
        print("Database initialization complete.")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        # Decide if the app should exit or continue without DB

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Watchdog API"} 