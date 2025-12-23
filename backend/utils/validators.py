from fastapi import HTTPException


# BASIC STRING VALIDATION

def require_non_empty(value: str, field_name: str):
    """
    Ensures a string is not empty or whitespace.
    """
    if not isinstance(value, str) or not value.strip():
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} cannot be empty"
        )
    return value.strip()


def require_length(value: str, field_name: str, min_len=1, max_len=100):
    """
    Ensures a string value meets length requirements.
    """
    if not (min_len <= len(value) <= max_len):
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be between {min_len} and {max_len} characters"
        )
    return value


# VOTER ID VALIDATION

def validate_voter_id(voter_id: str):
    """
    Basic voter ID validation:
      - must be alphanumeric
      - non-empty
      - reasonable length
    """
    voter_id = require_non_empty(voter_id, "Voter ID")
    require_length(voter_id, "Voter ID", 3, 32)

    if not voter_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(
            status_code=400,
            detail="Voter ID must be alphanumeric (underscores and hyphens allowed)"
        )

    return voter_id


# CANDIDATE NAME VALIDATION

def validate_candidate_name(name: str):
    """
    Candidate names must be:
      - non-empty
      - alphabetic (spaces allowed)
    """
    name = require_non_empty(name, "Candidate name")
    require_length(name, "Candidate name", 2, 50)

    if not all(ch.isalpha() or ch == " " for ch in name):
        raise HTTPException(
            status_code=400,
            detail="Candidate name must contain only letters and spaces"
        )

    return name.strip()


# ELECTION STATUS VALIDATION

def validate_election_action(status, action: str):
    """
    Validates whether a given election action (start/vote/end)
    is allowed based on current status.
    """
    if action == "start" and status != "NOT_STARTED":
        raise HTTPException(
            status_code=400,
            detail="Election cannot be started again"
        )

    if action == "vote" and status != "ONGOING":
        raise HTTPException(
            status_code=403,
            detail="Voting is not allowed at this time"
        )

    if action == "end" and status != "ONGOING":
        raise HTTPException(
            status_code=400,
            detail="Election is not currently running"
        )

    return True
