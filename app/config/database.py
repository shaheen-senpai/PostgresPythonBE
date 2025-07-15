"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.config.settings import get_settings

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    str(get_settings().DATABASE_URI),
    pool_pre_ping=True,  # Enables connection health checks
    pool_size=5,         # Number of connections to keep open
    max_overflow=10,     # Max number of connections to create beyond pool_size
    pool_timeout=30,     # Seconds to wait before giving up on getting a connection
    pool_recycle=1800,   # Recycle connections after 30 minutes
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db() -> Session:
    """
    Get database session dependency.
    
    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
