import time
import jwt
from fastapi import HTTPException


# JWT CONFIG

SECRET_KEY = "VOTECHAIN_LOCAL_SECRET"   # replace with env variable in prod
ALGORITHM = "HS256"


# CREATE TOKEN

def create_token(identity: str, role: str) -> str:
    """
    Create a signed JWT.
    identity: voter_id or "admin"
    role: "voter" or "admin"
    """
    payload = {
        "sub": identity,
        "role": role,
        "iat": int(time.time())
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# DECODE TOKEN

def decode_token(token: str):
    """
    Returns (identity, role) extracted from token.
    Raises HTTPException on invalid or expired tokens.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"], payload["role"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# QUICK VALIDATOR: CONFIRM ADMIN

def is_admin(token: str) -> bool:
    identity, role = decode_token(token)
    return role == "admin"


# QUICK VALIDATOR: CONFIRM VOTER

def is_voter(token: str):
    """
    Returns voter_id if token belongs to a voter.
    """
    identity, role = decode_token(token)
    if role != "voter":
        raise HTTPException(status_code=403, detail="Voter access required")
    return identity
