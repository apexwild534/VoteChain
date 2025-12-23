import pytest
from backend.blockchain.chain import Blockchain
from backend.blockchain.transaction import VoteTransaction
from backend.blockchain.utils import sha256_hash
from backend.blockchain.block import Block


# FIXTURE: Fresh blockchain for every test

@pytest.fixture
def chain():
    return Blockchain()


# GENESIS BLOCK TESTS

def test_genesis_block_exists(chain):
    assert len(chain.chain) == 1
    genesis = chain.chain[0]

    assert genesis.index == 0
    assert genesis.previous_hash == "0"
    assert isinstance(genesis.hash, str)
    assert genesis.transactions == []


def test_genesis_block_hash_is_valid(chain):
    genesis = chain.chain[0]
    recalculated = genesis.compute_hash()
    assert genesis.hash == recalculated


# TRANSACTION + MINING TESTS

def test_add_transaction(chain):
    tx = VoteTransaction(voter_hash="hash1", candidate_id=1)
    chain.add_transaction(tx)

    assert len(chain.current_transactions) == 1
    assert chain.current_transactions[0].voter_hash == "hash1"


def test_mine_block_creates_new_block(chain):
    tx = VoteTransaction(voter_hash="hash123", candidate_id=2)
    chain.add_transaction(tx)

    new_block = chain.mine_block()

    assert new_block is not None
    assert len(chain.chain) == 2
    assert new_block.index == 1
    assert len(new_block.transactions) == 1


def test_mining_clears_pending_transactions(chain):
    tx = VoteTransaction(voter_hash="abc", candidate_id=2)
    chain.add_transaction(tx)

    chain.mine_block()

    assert chain.current_transactions == []


# CHAIN VALIDATION TESTS

def test_chain_valid_initially(chain):
    assert chain.is_chain_valid() == True


def test_invalid_previous_hash_detected(chain):
    tx = VoteTransaction("h1", 1)
    chain.add_transaction(tx)
    chain.mine_block()

    # Tamper with the block
    chain.chain[1].previous_hash = "X_INVALID"

    assert chain.is_chain_valid() == False


def test_data_tampering_breaks_hash(chain):
    tx = VoteTransaction("hh22", 1)
    chain.add_transaction(tx)
    chain.mine_block()

    # Tamper data inside block
    chain.chain[1].transactions[0].candidate_id = 999

    assert chain.is_chain_valid() == False


# HASH CONSISTENCY TEST

def test_hash_is_deterministic():
    data = {"index": 1, "value": "test"}
    h1 = sha256_hash(data)
    h2 = sha256_hash(data)

    assert h1 == h2       # deterministic
    assert isinstance(h1, str)


# CONSENSUS TEST (BASIC LONGEST CHAIN)

def test_consensus_picks_longest_chain(chain):
    # Base chain has 1 block (genesis)
    # Build a longer chain
    chain2 = Blockchain()

    tx1 = VoteTransaction("A", 1)
    tx2 = VoteTransaction("B", 2)

    chain2.add_transaction(tx1)
    chain2.mine_block()

    chain2.add_transaction(tx2)
    chain2.mine_block()   # Now chain2 has 3 blocks

    # chain.resolve_conflicts expects list of chains
    changed = chain.resolve_conflicts([chain2])

    assert changed == True
    assert len(chain.chain) == 3   # adopted longer chain


def test_consensus_rejects_invalid_chain(chain):
    # Create another chain
    chain2 = Blockchain()

    chain2.add_transaction(VoteTransaction("X", 1))
    chain2.mine_block()

    # Tamper it
    chain2.chain[1].previous_hash = "WRONG"

    changed = chain.resolve_conflicts([chain2])

    # Should NOT adopt invalid chain
    assert changed == False
    assert len(chain.chain) == 1
