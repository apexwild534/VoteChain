import hashlib
import json
import time


# --------------------------------------------------------
# SHA-256 HASHING
# --------------------------------------------------------

def sha256_hash(data) -> str:
    """
    Takes any JSON-serializable object and returns
    a SHA-256 hex digest.

    Used to:
      - hash block contents
      - hash structured blockchain data
    """
    json_string = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(json_string).hexdigest()


# --------------------------------------------------------
# JSON-READY SERIALIZATION
# --------------------------------------------------------

def serialize_transactions(transactions):
    """
    Converts a list of VoteTransaction objects into
    a list of dictionaries ready for hashing.

    This avoids depending on Python internal attributes.
    """
    return [tx.to_dict() for tx in transactions]


# --------------------------------------------------------
# TIMESTAMP UTILITY
# --------------------------------------------------------

def current_timestamp() -> float:
    """
    Unified timestamp function, useful for:
      - block creation
      - transaction creation
      - audit logs
    """
    return time.time()


# --------------------------------------------------------
# BLOCK DATA NORMALIZER
# --------------------------------------------------------

def prepare_block_data(index, timestamp, transactions, previous_hash):
    """
    Takes the raw components of a block and returns a clean,
    JSON-serializable dictionary ready to be hashed.

    This is used by Block.compute_hash().
    """
    return {
        "index": index,
        "timestamp": timestamp,
        "transactions": serialize_transactions(transactions),
        "previous_hash": previous_hash
    }
