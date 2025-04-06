"""
Main FastAPI application for the Watchdog backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from starlette.staticfiles import StaticFiles as StarletteStaticFiles

# Import from consolidated modules
from .api import router as api_router # Import the single router
from .db import init_db
from .core import APP_DIR, get_list_of_states # Import APP_DIR and get_list_of_states

app = FastAPI(
    title="Watchdog API",
    description="API for the Watchdog congressional monitoring platform",
    version="1.0.0"
)

# Custom static files handler with caching headers
class CachedStaticFiles(StarletteStaticFiles):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            # Add caching headers: cache for 1 day
            response.headers.append('Cache-Control', 'public, max-age=86400')
        return response

# Mount static files directory (for images) with caching enabled
static_dir = APP_DIR / "static"
app.mount("/static", CachedStaticFiles(directory=static_dir), name="static")

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

# Endpoint to serve the list of states
@app.get("/api/congress/states", tags=["congress"])
async def get_states_list():
    """Returns a list of US states."""
    return get_list_of_states()

# Fallback handler for missing images
@app.get("/static/images/{image_path:path}")
async def get_image_or_placeholder(image_path: str):
    """Serve a placeholder image if the requested image is not found."""
    try:
        # Normalize the path and avoid path traversal
        image_path = os.path.normpath(image_path).lstrip("/")
        full_path = static_dir / "images" / image_path
        placeholder_path = static_dir / "images" / "placeholder.png"
        
        # Ensure placeholder exists
        if not os.path.exists(placeholder_path):
            print(f"WARNING: Placeholder image missing at {placeholder_path}")
            return {"error": "Placeholder image not found"}, 500
        
        # Try to serve the requested image
        if os.path.exists(full_path) and os.path.isfile(full_path):
            # Check if it's a valid image file
            if full_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                return FileResponse(
                    full_path, 
                    headers={
                        "Cache-Control": "public, max-age=86400",
                        "Content-Type": "image/jpeg" if full_path.suffix.lower() in ['.jpg', '.jpeg'] else "image/png"
                    }
                )
        
        # If image not found or invalid, return placeholder
        print(f"Image not found, serving placeholder: {image_path}")
        return FileResponse(
            placeholder_path,
            headers={
                "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                "Content-Type": "image/png"
            }
        )
    except Exception as e:
        print(f"Error serving image {image_path}: {e}")
        # Last resort - try to send placeholder without custom headers
        try:
            return FileResponse(placeholder_path)
        except:
            return {"error": "Image delivery failed"}, 500 