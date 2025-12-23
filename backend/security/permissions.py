from fastapi import HTTPException
from ..routes.auth import get_current_user


# REQUIRE ADMIN ACCESS

def require_admin(token: str = ""):
    """
    Ensures the provided JWT token belongs to an admin.
    Returns True if allowed, raises HTTPException if not.
    """
    identity, role = get_current_user(token)

    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return True


# REQUIRE VOTER ACCESS

def require_voter(token: str = ""):
    """
    Ensures the provided JWT token belongs to a voter.
    Returns the voter_id if allowed.
    """
    identity, role = get_current_user(token)

    if role != "voter":
        raise HTTPException(status_code=403, detail="Voter access required")

    return identity   # voter_id


# REQUIRE EITHER ROLE (READ-ONLY ACCESS)

def require_any_user(token: str = ""):
    """
    Allows both admin and voter users.
    Returns tuple (identity, role).
    Useful for endpoints that are public to all authenticated users.
    """
    identity, role = get_current_user(token)
    return identity, role
