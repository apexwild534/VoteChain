from sqlalchemy import Column, Integer, String, Boolean, Enum
import enum

from .session import Base   # ✅ IMPORT THE SAME BASE


class ElectionStatus(enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    ONGOING = "ONGOING"
    ENDED = "ENDED"


class Voter(Base):
    __tablename__ = "voters"

    id = Column(Integer, primary_key=True, index=True)

    voter_id = Column(String, unique=True, nullable=False)
    voter_hash = Column(String, unique=True, nullable=False)

    has_voted = Column(Boolean, default=False)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class ElectionState(Base):
    __tablename__ = "election_state"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(ElectionStatus), default=ElectionStatus.NOT_STARTED)