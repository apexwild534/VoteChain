import time


class VoteTransaction:
    """
    A single vote event.
    Stores the hashed voter ID and the candidate they selected.
    """

    def __init__(self, voter_hash, candidate_id):
        self.voter_hash = voter_hash              # anonymized voter identity
        self.candidate_id = candidate_id          # integer or UUID
        self.timestamp = time.time()              # vote creation time

    def to_dict(self):
        """
        Serialize the transaction for block hashing.
        """
        return {
            "voter_hash": self.voter_hash,
            "candidate_id": self.candidate_id,
            "timestamp": self.timestamp
        }
