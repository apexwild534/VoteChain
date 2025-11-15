from .utils import (
    sha256_hash,
    prepare_block_data,
    current_timestamp
)


class Block:
    """
    A single block in the VoteChain blockchain.
    Stores:
      - index
      - timestamp
      - list of VoteTransaction objects
      - previous_hash
      - own hash (automatically computed)
    """

    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = current_timestamp()
        self.transactions = transactions          # list of VoteTransaction objects
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        """
        Convert block contents into a normalized JSON dict
        and hash it with SHA-256.
        """
        block_data = prepare_block_data(
            index=self.index,
            timestamp=self.timestamp,
            transactions=self.transactions,
            previous_hash=self.previous_hash
        )

        return sha256_hash(block_data)
