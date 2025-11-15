import hashlib
import time
import jwt
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..database.crud import get_voter_by_id
from ..database.models import ElectionStatus


# Secret key for signing tokens
SECRET_KEY = "VOTECHAIN_LOCAL_SECRET"
ALGORITHM = "HS256"


# ------------------------------------------------
# HELPER: hash a voter_id for blockchain anonymity
# ------------------------------------------------
def hash_voter_id(voter_id: str) -> str:
    """
    Hash the voter's login ID using SHA-256.
    This result is stored and used in VoteTransaction.
    """
    return hashlib.sha256(voter_id.encode()).hexdigest()


# ------------------------------------------------
# HELPER: create JWT token
# ------------------------------------------------
def create_token(identity: str, role: str):
    """
    identity = voter_id or 'admin'
    role = 'admin' or 'voter'
    """
    payload = {
        "sub": identity,
        "role": role,
        "iat": time.time()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ------------------------------------------------
# ADMIN LOGIN (simple password)
# ------------------------------------------------
def admin_login(password: str):
    """
    Local-only admin login.
    You can later store admin credentials in DB or environment.
    """
    ADMIN_PASSWORD = "admin123"   # replace with env variable later

    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password")

    token = create_token("admin", "admin")
    return {"token": token}


# ------------------------------------------------
# VOTER LOGIN
# ------------------------------------------------
def voter_login(voter_id: str, db: Session = Depends(get_db)):
    """
    Voter logs in using their voter_id.
    Returns a JWT token if valid.
    """
    voter = get_voter_by_id(db, voter_id)
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")

    token = create_token(voter_id, "voter")
    return {"token": token}


# ------------------------------------------------
# TOKEN DECODER (admin or voter)
# ------------------------------------------------
def get_current_user(token: str):
    """
    Decode token and return identity + role.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"], payload["role"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
