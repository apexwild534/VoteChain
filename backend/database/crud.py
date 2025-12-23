from sqlalchemy.orm import Session
from .models import Voter, Candidate, ElectionState, ElectionStatus
from sqlalchemy.exc import IntegrityError


# -----------------------------
# VOTERS
# -----------------------------

def register_voter(db: Session, voter_id: str, voter_hash: str):
    """
    Registers a new voter.
    voter_id = used for login
    voter_hash = hash used for blockchain transactions
    """
    voter = Voter(voter_id=voter_id, voter_hash=voter_hash)

    db.add(voter)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None  # voter_id or voter_hash already exists

    db.refresh(voter)
    return voter


def get_voter_by_id(db: Session, voter_id: str):
    return db.query(Voter).filter(Voter.voter_id == voter_id).first()


def get_all_voters(db: Session):
    return db.query(Voter).all()


def mark_voter_as_voted(db: Session, voter_id: str):
    voter = get_voter_by_id(db, voter_id)
    if not voter:
        return False

    voter.has_voted = True
    db.commit()
    return True

def get_all_voters(db: Session):
    return db.query(Voter).all()


# -----------------------------
# CANDIDATES
# -----------------------------

def add_candidate(db: Session, name: str):
    candidate = Candidate(name=name)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def delete_candidate(db: Session, candidate_id: int):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        return False

    db.delete(candidate)
    db.commit()
    return True


def update_candidate_name(db: Session, candidate_id: int, new_name: str):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        return None

    candidate.name = new_name
    db.commit()
    db.refresh(candidate)
    return candidate


def get_all_candidates(db: Session):
    return db.query(Candidate).all()


# -----------------------------
# ELECTION STATE
# -----------------------------

def get_election_state(db: Session):
    """
    Returns the single election state row.
    If it doesn't exist, create it.
    """
    state = db.query(ElectionState).first()

    if not state:
        state = ElectionState(status=ElectionStatus.NOT_STARTED)
        db.add(state)
        db.commit()
        db.refresh(state)

    return state


def set_election_status(db: Session, new_status: ElectionStatus):
    state = get_election_state(db)
    state.status = new_status
    db.commit()
    return state


def reset_voters(db: Session):
    """
    Clears 'has_voted' flags for all voters.
    Useful when starting a new election.
    """
    db.query(Voter).update({Voter.has_voted: False})
    db.commit()
