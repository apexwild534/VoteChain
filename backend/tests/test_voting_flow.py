import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.database.session import SessionLocal
from backend.database.crud import add_voter, add_candidate

client = TestClient(app)


# ---------------------------------------------------------
# FIXTURE: Setup election with sample data
# ---------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def setup_data():
    """Ensure voter + candidates exist before tests."""
    db = SessionLocal()

    # Voter for testing
    try:
        add_voter(db, "FLOWTEST001")
    except Exception:
        pass

    # Candidates for testing
    try:
        add_candidate(db, "Candidate A")
        add_candidate(db, "Candidate B")
    except Exception:
        pass

    db.close()


# ---------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------

@pytest.fixture
def admin_token():
    res = client.post("/admin/login?password=admin123")
    assert res.status_code == 200
    return res.json()["token"]


@pytest.fixture
def voter_token():
    res = client.post("/voter/login?voter_id=FLOWTEST001")
    assert res.status_code == 200
    return res.json()["token"]


# ---------------------------------------------------------
# VOTING FLOW TESTS
# ---------------------------------------------------------

def test_start_election(admin_token):
    """Admin starts the election."""
    res = client.post("/admin/election/start", headers={"Authorization": admin_token})
    assert res.status_code == 200
    assert res.json()["status"] == "ONGOING"


def test_voter_can_fetch_candidates(voter_token):
    """Voter must see candidate list."""
    res = client.get("/voter/candidates", headers={"Authorization": voter_token})
    assert res.status_code == 200
    assert "candidates" in res.json()
    assert len(res.json()["candidates"]) >= 1


def test_voter_casts_vote_successfully(voter_token):
    """Voter casts vote normally."""
    # Get candidates
    cand_res = client.get("/voter/candidates", headers={"Authorization": voter_token})
    candidates = cand_res.json()["candidates"]
    candidate_id = candidates[0]["id"]

    res = client.post(f"/voter/vote/{candidate_id}", headers={"Authorization": voter_token})
    assert res.status_code == 200
    assert "Vote cast successfully" in res.json()["message"]


def test_voter_cannot_vote_twice(voter_token):
    """Second vote MUST fail."""
    # Try voting again with same token
    res = client.post("/voter/vote/1", headers={"Authorization": voter_token})
    assert res.status_code == 400 or res.status_code == 403
    assert "already voted" in res.json()["detail"].lower()


def test_blockchain_has_at_least_one_block_after_voting(admin_token):
    """After voting, blockchain must have 2+ blocks (genesis + mined blocks)."""
    res = client.get("/admin/blockchain", headers={"Authorization": admin_token})
    assert res.status_code == 200

    chain = res.json()["chain"]
    assert len(chain) >= 2      # genesis + at least one mined block


def test_end_election(admin_token):
    """Admin ends the election."""
    res = client.post("/admin/election/end", headers={"Authorization": admin_token})
    assert res.status_code == 200
    assert res.json()["status"] == "ENDED"


def test_results_available_after_election(admin_token):
    """Once election ends, results must be available."""
    res = client.get("/admin/results", headers={"Authorization": admin_token})
    assert res.status_code == 200
    data = res.json()

    assert "results" in data
    assert len(data["results"]) >= 1
    assert data["total_votes"] >= 1
