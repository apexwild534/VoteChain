from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .chain import Blockchain


class ConsensusEngine:
    """
    A simple consensus engine for VoteChain.
    This is NOT PoW/PoS — it's a lightweight mechanism suitable for
    a trusted local environment.

    It handles:
      - validating chains
      - resolving forks by choosing the longest valid chain
      - safe block addition
    """

    def __init__(self, blockchain):
        # blockchain is an INSTANCE, not the class
        self.local_chain = blockchain

    # --------------------------------------------------------
    # CHAIN VALIDATION
    # --------------------------------------------------------

    def validate_chain(self, chain) -> bool:
        """
        Ensures a candidate chain is valid.
        """
        return chain.is_chain_valid()

    # --------------------------------------------------------
    # FORK RESOLUTION: LONGEST VALID CHAIN WINS
    # --------------------------------------------------------

    def resolve_conflicts(self, candidate_chains: List["Blockchain"]) -> bool:
        """
        Picks the longest valid chain from candidates.
        """
        longest_chain = self.local_chain
        max_length = len(self.local_chain.chain)

        for chain in candidate_chains:
            if (
                len(chain.chain) > max_length
                and self.validate_chain(chain)
            ):
                longest_chain = chain
                max_length = len(chain.chain)

        if longest_chain is not self.local_chain:
            self.local_chain = longest_chain
            return True

        return False

    # --------------------------------------------------------
    # ADD BLOCK SAFELY
    # --------------------------------------------------------

    def add_block_to_chain(self, block) -> bool:
        """
        Appends block only if it correctly follows the last block.
        """
        last_block = self.local_chain.chain[-1]

        if block.previous_hash != last_block.hash:
            return False

        if block.hash != block.compute_hash():
            return False

        self.local_chain.chain.append(block)
        return True

    # --------------------------------------------------------
    # ACCESSOR
    # --------------------------------------------------------

    def get_chain(self):
        return self.local_chain
