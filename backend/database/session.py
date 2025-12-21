import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# --------------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------------

DATABASE_URL = os.getenv(
    "VOTECHAIN_DB",
    "sqlite:///./votechain.db"   # safe fallback
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

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
