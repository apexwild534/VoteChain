from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..database.crud import (
    get_voter_by_id,
    get_all_candidates,
    mark_voter_as_voted,
    get_election_state
)
from ..database.models import ElectionStatus

from ..blockchain.chain import Blockchain
from ..blockchain.transaction import VoteTransaction
from ..routes.auth import get_current_user, hash_voter_id

from ..routes.admin_routes import blockchain   # same instance as admin

router = APIRouter(prefix="/voter")


# -----------------------------
# AUTH GUARD
# -----------------------------

def verify_voter(token: str = ""):
    """
    Confirms the token belongs to a voter.
    Returns the voter_id for convenience.
    """
    identity, role = get_current_user(token)
    if role != "voter":
        raise HTTPException(status_code=403, detail="Voter access required")
    return identity   # voter_id


# -----------------------------
# VIEW CANDIDATES (names only)
# -----------------------------

@router.get("/candidates")
def voter_view_candidates(
    db: Session = Depends(get_db),
    voter_id: str = Depends(verify_voter)
):
    candidates = get_all_candidates(db)

    result = [{"id": c.id, "name": c.name} for c in candidates]
    return {"candidates": result}


# -----------------------------
# CAST VOTE
# -----------------------------

@router.post("/vote/{candidate_id}")
def voter_cast_vote(
    candidate_id: int,
    db: Session = Depends(get_db),
    voter_id: str = Depends(verify_voter)
):
    # Check election status
    state = get_election_state(db)

    if state.status != ElectionStatus.ONGOING:
        raise HTTPException(status_code=403, detail="Election not ongoing now")

    # Get voter and ensure they haven't voted
    voter = get_voter_by_id(db, voter_id)
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")

    if voter.has_voted:
        raise HTTPException(status_code=400, detail="This voter has already voted")

    # Make sure candidate exists
    candidates = get_all_candidates(db)
    candidate_ids = [c.id for c in candidates]
    if candidate_id not in candidate_ids:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Create anonymous blockchain transaction
    hashed = hash_voter_id(voter_id)
    tx = VoteTransaction(voter_hash=hashed, candidate_id=candidate_id)

    blockchain.add_transaction(tx)

    # Mark voter as having voted
    mark_voter_as_voted(db, voter_id)

    return {"message": "Vote cast successfully"}


# -----------------------------
# VIEW RESULTS (after election ends)
# -----------------------------

@router.get("/results")
def voter_view_results(
    db: Session = Depends(get_db),
    voter_id: str = Depends(verify_voter)
):
    state = get_election_state(db)

    if state.status != ElectionStatus.ENDED:
        raise HTTPException(status_code=403, detail="Election results not available")

    # Use admin logic for consistent results
    candidates = get_all_candidates(db)

    vote_counts = {c.id: 0 for c in candidates}

    # count votes from blockchain
    for block in blockchain.chain:
        for tx in block.transactions:
            vote_counts[tx.candidate_id] = vote_counts.get(tx.candidate_id, 0) + 1

    total_votes = sum(vote_counts.values())

    result = []
    for c in candidates:
        votes = vote_counts[c.id]
        pct = (votes / total_votes * 100) if total_votes > 0 else 0

        result.append({
            "candidate": c.name,
            "votes": votes,
            "percent_of_votes": round(pct, 2)
        })

    return {
        "total_votes": total_votes,
        "results": result
    }
