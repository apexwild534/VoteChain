import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.database.session import SessionLocal
from backend.database.models import Voter
from backend.database.crud import add_voter

client = TestClient(app)


# Helper: Create test voter

@pytest.fixture(scope="module", autouse=True)
def setup_test_voter():
    db = SessionLocal()
    add_voter(db, "TESTVOTER")
    db.close()


# Admin Login Tests

def test_admin_login_success():
    res = client.post("/admin/login?password=admin123")
    assert res.status_code == 200
    assert "token" in res.json()


def test_admin_login_failure():
    res = client.post("/admin/login?password=wrongpass")
    assert res.status_code == 401


# Voter Login Tests

def test_voter_login_success():
    res = client.post("/voter/login?voter_id=TESTVOTER")
    assert res.status_code == 200
    assert "token" in res.json()


def test_voter_login_invalid():
    res = client.post("/voter/login?voter_id=INVALID123")
    assert res.status_code in [400, 404]   # depending on your implementation


# Permission & Token Tests

def test_voter_cannot_access_admin_route():
    # login voter
    vlogin = client.post("/voter/login?voter_id=TESTVOTER")
    token = vlogin.json()["token"]

    res = client.get(
        "/admin/voters/count",
        headers={"Authorization": token}
    )

    assert res.status_code == 403   # voter forbidden


def test_admin_can_access_admin_route():
    # login admin
    alogin = client.post("/admin/login?password=admin123")
    token = alogin.json()["token"]

    res = client.get(
        "/admin/voters/count",
        headers={"Authorization": token}
    )

    assert res.status_code in (200, 202)  # count endpoint returns valid response


def test_protected_voter_route_requires_token():
    res = client.get("/voter/candidates")
    assert res.status_code == 401


def test_token_decoding_and_identity():
    # login voter
    vlogin = client.post("/voter/login?voter_id=TESTVOTER")
    token = vlogin.json()["token"]

    # call a voter-protected route
    res = client.get(
        "/voter/candidates",
        headers={"Authorization": token}
    )

    # Should be allowed
    assert res.status_code == 200
