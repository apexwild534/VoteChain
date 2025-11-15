from .block import Block
from .transaction import VoteTransaction
from .utils import serialize_transactions
from .consensus import ConsensusEngine


class Blockchain:
    """
    Core VoteChain blockchain:
      - holds blocks
      - queues transactions until mining
      - validates chain through ConsensusEngine
    """

    def __init__(self):
        # internal blocks
        self.chain = []
        # unmined VoteTransaction objects
        self.current_transactions = []

        # simple local consensus engine
        self.consensus = ConsensusEngine()

        # initialize genesis
        self.create_genesis_block()

    # --------------------------------------------------------
    # GENESIS BLOCK
    # --------------------------------------------------------

    def create_genesis_block(self):
        """
        Creates the very first block with:
          index = 0
          empty transaction list
          previous hash = "0"
        """
        genesis = Block(
            index=0,
            transactions=[],
            previous_hash="0"
        )
        self.chain.append(genesis)

    # --------------------------------------------------------
    # TRANSACTION MANAGEMENT
    # --------------------------------------------------------

    def add_transaction(self, vote_tx: VoteTransaction):
        """
        Add a vote transaction to the pending list.
        vote_tx is a VoteTransaction instance.
        """
        self.current_transactions.append(vote_tx)

    # --------------------------------------------------------
    # BLOCK CREATION (MINING)
    # --------------------------------------------------------

    def mine_block(self):
        """
        Turns current transactions into a new block,
        appends it to the chain, and clears the mempool.
        """
        if not self.current_transactions:
            return None

        last_block = self.chain[-1]

        new_block = Block(
            index=len(self.chain),
            transactions=self.current_transactions.copy(),
            previous_hash=last_block.hash
        )

        # add block to chain (through consensus engine hook)
        self.chain.append(new_block)

        # clear pending tx
        self.current_transactions = []

        return new_block

    # --------------------------------------------------------
    # CHAIN VALIDATION
    # --------------------------------------------------------

    def is_chain_valid(self) -> bool:
        """
        Validate the entire chain using the consensus engine.
        """
        return self.consensus.validate_chain(self)

    # --------------------------------------------------------
    # CHAIN STATE HELPERS
    # --------------------------------------------------------

    def get_pending_transactions(self):
        """
        Returns the list of unmined transactions.
        """
        return serialize_transactions(self.current_transactions)

    def length(self):
        return len(self.chain)

    def last_block(self):
        return self.chain[-1]


    # --------------------------------------------------------
    # OPTIONAL SYNC (multi-node future support)
    # --------------------------------------------------------

    def resolve_conflicts(self, other_chains: list):
        """
        Accepts multiple chains and adopts the longest valid one.
        """
        changed = self.consensus.resolve_conflicts(other_chains)
        if changed:
            self.chain = self.consensus.get_chain().chain
        return changed
