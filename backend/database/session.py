from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# --------------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------------

# Using SQLite for simplicity; replace with PostgreSQL/MySQL if needed.
DATABASE_URL = "sqlite:///./votechain.db"

# For SQLite: check_same_thread=False is required for FastAPI background threads.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create a session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()


# --------------------------------------------------------
# SESSION DEPENDENCY FOR FASTAPI
# --------------------------------------------------------

def get_db():
    """
    Provides a database session to any FastAPI endpoint.
    Ensures the session is closed after request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
