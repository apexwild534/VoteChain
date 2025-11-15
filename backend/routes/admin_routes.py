from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..database.crud import (
    add_candidate,
    delete_candidate,
    update_candidate_name,
    get_all_candidates,
    get_all_voters,
    set_election_status,
    get_election_state,
    reset_voters
)
from ..database.models import ElectionStatus

from ..blockchain.chain import Blockchain
from ..routes.auth import get_current_user

# Local blockchain instance (in-memory)
blockchain = Blockchain()

router = APIRouter(prefix="/admin")


# -----------------------------
# AUTH GUARD
# -----------------------------

def verify_admin(token: str = ""):
    """
    Confirms the token belongs to an admin.
    """
    identity, role = get_current_user(token)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return True


# -----------------------------
# CANDIDATE MANAGEMENT
# -----------------------------

@router.post("/candidate/add")
def admin_add_candidate(name: str, db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    return add_candidate(db, name)


@router.delete("/candidate/delete/{candidate_id}")
def admin_delete_candidate(candidate_id: int, db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    ok = delete_candidate(db, candidate_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"message": "Candidate deleted"}


@router.put("/candidate/update/{candidate_id}")
def admin_update_candidate(candidate_id: int, new_name: str, db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    candidate = update_candidate_name(db, candidate_id, new_name)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


# -----------------------------
# VIEW REGISTERED VOTERS (count only)
# -----------------------------

@router.get("/voters/count")
def admin_voter_count(db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    voters = get_all_voters(db)
    return {"registered_voters": len(voters)}


# -----------------------------
# VIEW CANDIDATE LIST
# -----------------------------

@router.get("/candidates")
def admin_candidates(db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    return get_all_candidates(db)


# -----------------------------
# START ELECTION
# -----------------------------

@router.post("/election/start")
def admin_start_election(db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    state = get_election_state(db)

    if state.status == ElectionStatus.ONGOING:
        raise HTTPException(status_code=400, detail="Election already ongoing")

    if state.status == ElectionStatus.NOT_STARTED:
        set_election_status(db, ElectionStatus.ONGOING)
        return {"message": "Election started"}

    if state.status == ElectionStatus.ENDED:
        raise HTTPException(status_code=400, detail="Election ended. Clear to start again.")


# -----------------------------
# END ELECTION (mines a block)
# -----------------------------

@router.post("/election/end")
def admin_end_election(db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    state = get_election_state(db)

    if state.status != ElectionStatus.ONGOING:
        raise HTTPException(status_code=400, detail="Election is not ongoing")

    # Mine the pending votes into a block
    blockchain.mine_block()

    set_election_status(db, ElectionStatus.ENDED)

    return {"message": "Election ended and votes sealed into blockchain."}


# -----------------------------
# VIEW RESULTS (only after end)
# -----------------------------

@router.get("/results")
def admin_view_results(db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    state = get_election_state(db)
    if state.status != ElectionStatus.ENDED:
        raise HTTPException(status_code=403, detail="Election not ended yet")

    candidates = get_all_candidates(db)
    voters = get_all_voters(db)

    vote_counts = {c.id: 0 for c in candidates}

    # Count votes from blockchain
    for block in blockchain.chain:
        for tx in block.transactions:
            vote_counts[tx.candidate_id] = vote_counts.get(tx.candidate_id, 0) + 1

    # Compute percentages
    total_votes = sum(vote_counts.values())
    total_voters = len(voters)

    result = []
    for c in candidates:
        votes = vote_counts.get(c.id, 0)

        pct_of_votes = (votes / total_votes * 100) if total_votes > 0 else 0
        pct_of_voters = (votes / total_voters * 100) if total_voters > 0 else 0

        result.append({
            "candidate": c.name,
            "votes": votes,
            "percent_of_votes": round(pct_of_votes, 2),
            "percent_of_registered_voters": round(pct_of_voters, 2)
        })

    turnout = (total_votes / total_voters * 100) if total_voters > 0 else 0

    return {
        "total_votes": total_votes,
        "voter_turnout_percent": round(turnout, 2),
        "results": result
    }


# -----------------------------
# CLEAR ELECTION
# -----------------------------

@router.post("/election/clear")
def admin_clear_election(db: Session = Depends(get_db), _: bool = Depends(verify_admin)):
    global blockchain

    # Reset blockchain
    blockchain = Blockchain()

    # Reset voters
    reset_voters(db)

    # Reset status
    set_election_status(db, ElectionStatus.NOT_STARTED)

    return {"message": "Election cleared and system reset."}
