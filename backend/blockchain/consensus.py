from .chain import Blockchain


class ConsensusEngine:
    """
    A simple consensus engine for VoteChain.
    This is NOT PoW/PoS — it's a lightweight mechanism suitable for
    a trusted local environment.

    It handles:
      - validating chains
      - resolving forks by choosing the longest valid chain
      - providing a hook to plug in more advanced consensus protocols later
    """

    def __init__(self):
        # In a multi-node setup, each node would have its own chain
        self.local_chain = Blockchain()

    # --------------------------------------------------------
    # CHAIN VALIDATION
    # --------------------------------------------------------

    def validate_chain(self, chain: Blockchain) -> bool:
        """
        Ensures a candidate chain is valid:
          - hashes intact
          - proper previous_hash linking
          - genesis block integrity
        """
        return chain.is_chain_valid()

    # --------------------------------------------------------
    # FORK RESOLUTION: LONGEST RULE
    # --------------------------------------------------------

    def resolve_conflicts(self, candidate_chains: list[Blockchain]):
        """
        Accepts a list of chains from other nodes (if any).
        Picks the longest **valid** chain.
        """
        longest_chain = self.local_chain
        max_length = len(self.local_chain.chain)

        for chain in candidate_chains:
            if len(chain.chain) > max_length and self.validate_chain(chain):
                longest_chain = chain
                max_length = len(chain.chain)

        # If a longer, valid chain is found, adopt it
        if longest_chain is not self.local_chain:
            self.local_chain = longest_chain
            return True

        return False

    # --------------------------------------------------------
    # ADD BLOCK TO LOCAL CHAIN SAFELY
    # --------------------------------------------------------

    def add_block_to_chain(self, block):
        """
        Only append block if previous_hash matches last block.
        Prevents tampering and accidental forks.
        """
        last_block = self.local_chain.chain[-1]

        if block.previous_hash != last_block.hash:
            return False

        # Final integrity check
        if block.hash != block.compute_hash():
            return False

        self.local_chain.chain.append(block)
        return True

    # --------------------------------------------------------
    # GET LOCAL CHAIN
    # --------------------------------------------------------

    def get_chain(self) -> Blockchain:
        """
        Returns the authoritative local chain.
        """
        return self.local_chain
