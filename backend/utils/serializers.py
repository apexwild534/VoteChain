from typing import List


# --------------------------------------------------------
# VOTER SERIALIZERS
# --------------------------------------------------------

def voter_to_dict(voter):
    """
    Serialize a Voter SQLAlchemy object for safe output.
    Note: voter_hash is intentionally excluded for privacy.
    """
    return {
        "id": voter.id,
        "voter_id": voter.voter_id,
        "has_voted": voter.has_voted
    }


def voters_list_to_dict(voters: List):
    return [voter_to_dict(v) for v in voters]


# --------------------------------------------------------
# CANDIDATE SERIALIZERS
# --------------------------------------------------------

def candidate_to_dict(candidate):
    return {
        "id": candidate.id,
        "name": candidate.name
    }


def candidates_list_to_dict(candidates: List):
    return [candidate_to_dict(c) for c in candidates]


# --------------------------------------------------------
# ELECTION RESULTS SERIALIZER
# --------------------------------------------------------

def election_result_entry(name: str, votes: int, pct_votes: float, pct_registered: float):
    """
    One row of the final result sheet.
    """
    return {
        "candidate": name,
        "votes": votes,
        "percent_of_votes": round(pct_votes, 2),
        "percent_of_registered_voters": round(pct_registered, 2)
    }


def full_election_results(total_votes: int, turnout_pct: float, rows: List[dict]):
    """
    Wraps the entire result calculation into a clean structure.
    """
    return {
        "total_votes": total_votes,
        "voter_turnout_percent": round(turnout_pct, 2),
        "results": rows
    }


# --------------------------------------------------------
# BLOCKCHAIN SERIALIZERS
# --------------------------------------------------------

def transaction_to_dict(tx):
    """
    Converts VoteTransaction into a dictionary suitable for
    blockchain inspection or debugging.
    """
    return {
        "voter_hash": tx.voter_hash,
        "candidate_id": tx.candidate_id,
        "timestamp": tx.timestamp
    }


def block_to_dict(block):
    """
    Converts a Block object into a JSON-safe structure.
    """
    return {
        "index": block.index,
        "timestamp": block.timestamp,
        "transactions": [transaction_to_dict(t) for t in block.transactions],
        "previous_hash": block.previous_hash,
        "hash": block.hash
    }


def chain_to_dict(chain):
    """
    Serializes the entire blockchain (useful if you build an admin debug page).
    """
    return [block_to_dict(b) for b in chain.chain]


# --------------------------------------------------------
# STANDARD API WRAPPERS
# --------------------------------------------------------

def success(message: str, data=None):
    return {
        "status": "success",
        "message": message,
        "data": data
    }


def error(message: str, code=None):
    return {
        "status": "error",
        "message": message,
        "code": code
    }
