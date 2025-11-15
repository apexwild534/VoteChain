from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..database.crud import get_election_state
from ..database.models import ElectionStatus


router = APIRouter(prefix="/election")


@router.get("/status")
def get_status(db: Session = Depends(get_db)):
    """
    A simple universal endpoint:
    - Voters use it to know if voting has begun
    - Admin uses it to confirm current state
    """
    state = get_election_state(db)

    return {
        "status": state.status.value  # NOT_STARTED, ONGOING, ENDED
    }
