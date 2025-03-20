from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
import os
import logging
import json
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import configuration
from config import DATABASE_URL

# Ensure the database directory exists
if DATABASE_URL.startswith('sqlite:///'):
    # Extract the path from the SQLite URL
    db_path = DATABASE_URL.replace('sqlite:///', '')
    directory = os.path.dirname(db_path)
    
    # Create the directory if it doesn't exist
    if directory and not os.path.exists(directory):
        logger.info(f"Creating database directory: {directory}")
        os.makedirs(directory, exist_ok=True)

# Create SQLAlchemy engine with connection arguments
if DATABASE_URL.startswith('sqlite:///'):
    # SQLite-specific connection arguments
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False  # Set to True to see SQL queries (useful for debugging)
    )
else:
    # For other database types (PostgreSQL, MySQL, etc.)
    engine = create_engine(DATABASE_URL)

# Create sessionmaker for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ----------------
# Database Models
# ----------------

class ApiConfig(Base):
    """Model for storing API configuration and credentials."""
    __tablename__ = "api_config"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    api_key = Column(String(100), nullable=True)
    base_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ApiConfig {self.name}>"

class User(Base):
    """User model for storing registered user information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    state = Column(String(2), index=True)
    subscribed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Add more models here as needed, for example:

class Representative(Base):
    """Model for storing information about representatives."""
    __tablename__ = "representatives"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    state = Column(String(2), index=True, nullable=False)
    district = Column(Integer, nullable=True)  # Only for House representatives
    party = Column(String(50), index=True)
    chamber = Column(String(10), index=True)  # 'House' or 'Senate'
    bio = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    twitter = Column(String(100), nullable=True)
    facebook = Column(String(100), nullable=True)
    congress_id = Column(String(50), index=True, unique=True, nullable=True)  # ID from Congress API
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    votes = relationship("Vote", back_populates="representative")

class Bill(Base):
    """Model for storing information about congressional bills."""
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    bill_number = Column(String(20), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), index=True)
    introduced_date = Column(DateTime, nullable=True)
    last_action_date = Column(DateTime, nullable=True)
    congress_session = Column(Integer, nullable=False)
    congress_id = Column(String(50), index=True, unique=True, nullable=True)  # ID from Congress API
    url = Column(String(255), nullable=True)  # URL to full bill text or details
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    votes = relationship("Vote", back_populates="bill")

class Vote(Base):
    """Model for storing voting records of representatives on bills."""
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    representative_id = Column(Integer, ForeignKey("representatives.id"), nullable=False)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    vote_position = Column(String(20), nullable=False)  # 'Yes', 'No', 'Present', 'Not Voting'
    vote_date = Column(DateTime, nullable=False)
    congress_vote_id = Column(String(50), index=True, nullable=True)  # ID from Congress API
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    representative = relationship("Representative", back_populates="votes")
    bill = relationship("Bill", back_populates="votes")

# Initialize database with all tables
def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized - all tables created")

# Call init_db to ensure tables are created
init_db()

# ----------------
# Pydantic Models
# ----------------

# User models for API interaction
class UserBase(BaseModel):
    """Base model for user data shared between create and update operations."""
    name: str
    email: str
    state: str
    subscribed: bool = False

class UserCreate(UserBase):
    """Model for creating a new user."""
    pass

class UserUpdate(BaseModel):
    """Model for updating an existing user with optional fields."""
    name: Optional[str] = None
    email: Optional[str] = None
    state: Optional[str] = None
    subscribed: Optional[bool] = None

class UserResponse(UserBase):
    """Model for user data returned from the API."""
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# API Config models
class ApiConfigBase(BaseModel):
    """Base model for API configuration data."""
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_active: bool = True

class ApiConfigCreate(ApiConfigBase):
    """Model for creating a new API configuration."""
    pass

class ApiConfigUpdate(BaseModel):
    """Model for updating an existing API configuration."""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_active: Optional[bool] = None

class ApiConfigResponse(ApiConfigBase):
    """Model for API configuration data returned from the API."""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Representative models
class RepresentativeBase(BaseModel):
    """Base model for representative data."""
    name: str
    state: str
    district: Optional[int] = None
    party: Optional[str] = None
    chamber: str
    bio: Optional[str] = None
    image_url: Optional[str] = None
    website: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    congress_id: Optional[str] = None

class RepresentativeResponse(RepresentativeBase):
    """Model for representative data returned from the API."""
    id: int
    last_updated: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Bill models
class BillBase(BaseModel):
    """Base model for bill data."""
    bill_number: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    introduced_date: Optional[datetime] = None
    last_action_date: Optional[datetime] = None
    congress_session: int
    congress_id: Optional[str] = None
    url: Optional[str] = None

class BillResponse(BillBase):
    """Model for bill data returned from the API."""
    id: int
    last_updated: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Vote models
class VoteBase(BaseModel):
    """Base model for vote data."""
    representative_id: int
    bill_id: int
    vote_position: str
    vote_date: datetime
    congress_vote_id: Optional[str] = None

class VoteResponse(VoteBase):
    """Model for vote data returned from the API."""
    id: int
    
    class Config:
        orm_mode = True

# ----------------
# Database Session
# ----------------

def get_db():
    """
    Dependency function that yields a database session.
    Ensures the session is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 