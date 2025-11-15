from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class ElectionStatus(enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    ONGOING = "ONGOING"
    ENDED = "ENDED"


class Voter(Base):
    __tablename__ = "voters"

    id = Column(Integer, primary_key=True, index=True)

    voter_id = Column(String, unique=True, nullable=False)   # real ID used for login
    voter_hash = Column(String, unique=True, nullable=False) # hashed ID stored for transactions

    has_voted = Column(Boolean, default=False)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class ElectionState(Base):
    __tablename__ = "election_state"

    id = Column(Integer, primary_key=True, index=True)

    status = Column(Enum(ElectionStatus), default=ElectionStatus.NOT_STARTED)
