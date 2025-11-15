import os
from pathlib import Path


# --------------------------------------------------------
# BASE PROJECT PATHS
# --------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


# --------------------------------------------------------
# DATABASE CONFIG
# --------------------------------------------------------

# SQLite for local deployments
DATABASE_URL = os.getenv(
    "VOTECHAIN_DB",
    f"sqlite:///{DATA_DIR / 'votechain.db'}"
)


# --------------------------------------------------------
# JWT / SECURITY CONFIG
# --------------------------------------------------------

SECRET_KEY = os.getenv("VOTECHAIN_SECRET_KEY", "VOTECHAIN_LOCAL_SECRET")
ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 60 * 60 * 12    # 12 hours, adjustable


# --------------------------------------------------------
# ADMIN CREDENTIALS (can move to DB later)
# --------------------------------------------------------

ADMIN_PASSWORD = os.getenv("VOTECHAIN_ADMIN_PASSWORD", "admin123")


# --------------------------------------------------------
# BLOCKCHAIN CONFIG
# --------------------------------------------------------

CHAIN_FILE = DATA_DIR / "chain.json"       # future persistence
AUTO_MINE_ON_END = True                    # mine block automatically when election ends
GENESIS_PREVIOUS_HASH = "0"


# --------------------------------------------------------
# ENVIRONMENT MODE
# --------------------------------------------------------

ENV = os.getenv("VOTECHAIN_ENV", "development")   # "development" or "production"


# --------------------------------------------------------
# FRONTEND CONFIG (if hosting static files)
# --------------------------------------------------------

STATIC_DIR = BASE_DIR / "frontend" / "static"
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
