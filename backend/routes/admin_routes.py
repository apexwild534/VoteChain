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
from ..routes.auth import get_current_user, admin_login


# ROUTER

router = APIRouter(prefix="/admin", tags=["Admin"])


# AUTH: ADMIN LOGIN

@router.post("/login")
def admin_login_route(password: str):
    """
    Returns a JWT token for admin access.
    """
    return admin_login(password)


# AUTH GUARD

def verify_admin(token: str = ""):
    """
    Confirms the token belongs to an admin.
    """
    identity, role = get_current_user(token)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return True


# LOCAL BLOCKCHAIN INSTANCE (in-memory)

blockchain = Blockchain()


# CANDIDATE MANAGEMENT

@router.post("/candidate/add")
def admin_add_candidate(
    name: str,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    return add_candidate(db, name)


@router.delete("/candidate/delete/{candidate_id}")
def admin_delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    ok = delete_candidate(db, candidate_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"message": "Candidate deleted"}


@router.put("/candidate/update/{candidate_id}")
def admin_update_candidate(
    candidate_id: int,
    new_name: str,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    candidate = update_candidate_name(db, candidate_id, new_name)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


# VIEW REGISTERED VOTERS (COUNT ONLY)

@router.get("/voters/count")
def admin_voter_count(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    voters = get_all_voters(db)
    return {"registered_voters": len(voters)}


# VIEW CANDIDATES

@router.get("/candidates")
def admin_candidates(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    return get_all_candidates(db)


# START ELECTION

@router.post("/election/start")
def admin_start_election(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    state = get_election_state(db)

    if state.status == ElectionStatus.ONGOING:
        raise HTTPException(status_code=400, detail="Election already ongoing")

    if state.status == ElectionStatus.ENDED:
        raise HTTPException(
            status_code=400,
            detail="Election ended. Clear election to start again."
        )

    set_election_status(db, ElectionStatus.ONGOING)
    return {"message": "Election started"}


# END ELECTION (MINES BLOCK)

@router.post("/election/end")
def admin_end_election(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    state = get_election_state(db)

    if state.status != ElectionStatus.ONGOING:
        raise HTTPException(status_code=400, detail="Election is not ongoing")

    blockchain.mine_block()
    set_election_status(db, ElectionStatus.ENDED)

    return {"message": "Election ended and votes sealed into blockchain"}


# VIEW RESULTS (POST-ELECTION)

@router.get("/results")
def admin_view_results(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    state = get_election_state(db)
    if state.status != ElectionStatus.ENDED:
        raise HTTPException(status_code=403, detail="Election not ended yet")

    candidates = get_all_candidates(db)
    voters = get_all_voters(db)

    vote_counts = {c.id: 0 for c in candidates}

    for block in blockchain.chain:
        for tx in block.transactions:
            vote_counts[tx.candidate_id] += 1

    total_votes = sum(vote_counts.values())
    total_voters = len(voters)

    results = []
    for c in candidates:
        votes = vote_counts.get(c.id, 0)

        results.append({
            "candidate": c.name,
            "votes": votes,
            "percent_of_votes": round((votes / total_votes * 100), 2) if total_votes else 0,
            "percent_of_registered_voters": round((votes / total_voters * 100), 2) if total_voters else 0
        })

    turnout = (total_votes / total_voters * 100) if total_voters else 0

    return {
        "total_votes": total_votes,
        "voter_turnout_percent": round(turnout, 2),
        "results": results
    }


# CLEAR ELECTION

@router.post("/election/clear")
def admin_clear_election(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    global blockchain

    blockchain = Blockchain()
    reset_voters(db)
    set_election_status(db, ElectionStatus.NOT_STARTED)

    return {"message": "Election cleared and system reset"}


#View Voters
@router.get("/voters")
def admin_view_voters(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    voters = get_all_voters(db)

    return [
        {
            "voter_id": v.voter_id
        }
        for v in voters
    ]

