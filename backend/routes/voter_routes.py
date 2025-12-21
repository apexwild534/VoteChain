from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..database.crud import (
    register_voter,
    get_voter_by_id,
    get_all_candidates,
    mark_voter_as_voted,
    get_election_state
)
from ..database.models import ElectionStatus

from ..blockchain.transaction import VoteTransaction
from ..routes.auth import (
    get_current_user,
    hash_voter_id,
    voter_login
)

# IMPORTANT: use the SAME blockchain instance as admin
from ..routes.admin_routes import blockchain

router = APIRouter(
    prefix="/voter",
    tags=["voter"]
)


# =========================================================
# AUTH GUARD
# =========================================================

def verify_voter(token: str = Query(...)):
    """
    Confirms the token belongs to a voter.
    Returns voter_id.
    """
    identity, role = get_current_user(token)
    if role != "voter":
        raise HTTPException(status_code=403, detail="Voter access required")
    return identity


# =========================================================
# VOTER REGISTRATION
# =========================================================

@router.post("/register")
def voter_register(
    voter_id: str,
    db: Session = Depends(get_db)
):
    voter_hash = hash_voter_id(voter_id)

    voter = register_voter(db, voter_id, voter_hash)
    if not voter:
        raise HTTPException(status_code=400, detail="Voter already exists")

    return {"message": "Voter registered successfully"}


# =========================================================
# VOTER LOGIN (JWT)
# =========================================================

@router.post("/login")
def voter_login_route(
    voter_id: str,
    db: Session = Depends(get_db)
):
    return voter_login(voter_id, db)


# =========================================================
# VIEW CANDIDATES
# =========================================================

@router.get("/candidates")
def voter_view_candidates(
    db: Session = Depends(get_db),
    voter_id: str = Depends(verify_voter)
):
    candidates = get_all_candidates(db)
    return {
        "candidates": [
            {"id": c.id, "name": c.name} for c in candidates
        ]
    }


# =========================================================
# CAST VOTE
# =========================================================

@router.post("/vote/{candidate_id}")
def voter_cast_vote(
    candidate_id: int,
    db: Session = Depends(get_db),
    voter_id: str = Depends(verify_voter)
):
    # Check election status
    state = get_election_state(db)
    if state.status != ElectionStatus.ONGOING:
        raise HTTPException(status_code=403, detail="Election not ongoing")

    # Get voter
    voter = get_voter_by_id(db, voter_id)
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")

    if voter.has_voted:
        raise HTTPException(status_code=400, detail="Voter has already voted")

    # Validate candidate
    candidates = get_all_candidates(db)
    if candidate_id not in [c.id for c in candidates]:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Create blockchain transaction
    voter_hash = hash_voter_id(voter_id)
    tx = VoteTransaction(
        voter_hash=voter_hash,
        candidate_id=candidate_id
    )

    blockchain.add_transaction(tx)

    # Mark voter as voted
    mark_voter_as_voted(db, voter_id)

    return {"message": "Vote cast successfully"}


# =========================================================
# VIEW RESULTS (AFTER ELECTION ENDS)
# =========================================================

@router.get("/results")
def voter_view_results(
    db: Session = Depends(get_db),
    voter_id: str = Depends(verify_voter)
):
    state = get_election_state(db)
    if state.status != ElectionStatus.ENDED:
        raise HTTPException(status_code=403, detail="Election results not available")

    candidates = get_all_candidates(db)
    vote_counts = {c.id: 0 for c in candidates}

    # Count votes from blockchain
    for block in blockchain.chain:
        for tx in block.transactions:
            vote_counts[tx.candidate_id] += 1

    total_votes = sum(vote_counts.values())

    results = []
    for c in candidates:
        votes = vote_counts[c.id]
        percent = (votes / total_votes * 100) if total_votes > 0 else 0

        results.append({
            "candidate": c.name,
            "votes": votes,
            "percent_of_votes": round(percent, 2)
        })

    return {
        "total_votes": total_votes,
        "results": results
    }