from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlmodel import create_engine as create_sqlmodel_engine
from typing import Optional
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment - NO FALLBACK to SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate DATABASE_URL before proceeding
# This will raise ValueError if DATABASE_URL is missing, invalid, or points to SQLite
from .validation import validate_database_url
validate_database_url(DATABASE_URL)

# For Neon PostgreSQL, ensure SSL is properly configured
if DATABASE_URL.startswith("postgresql://"):
    # For Neon, we may need to add SSL parameters
    if "?sslmode=" not in DATABASE_URL.lower():
        if "neon" in DATABASE_URL.lower():
            DATABASE_URL += "?sslmode=require"
        else:
            DATABASE_URL += "?sslmode=prefer"

# Create engine with appropriate settings for Neon
engine = create_sqlmodel_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Ensures connections are valid before use
    pool_recycle=300,    # Recycles connections every 5 minutes
    connect_args={
        "connect_timeout": 10,  # Timeout for connection attempts
    } if DATABASE_URL.startswith("postgresql://") else {}
)