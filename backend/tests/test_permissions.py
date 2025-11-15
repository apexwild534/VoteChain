import pytest
from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


# ------------------------------------------------------
# Helper: Get valid tokens
# ------------------------------------------------------

@pytest.fixture(scope="module")
def admin_token():
    res = client.post("/admin/login?password=admin123")
    assert res.status_code == 200
    return res.json()["token"]


@pytest.fixture(scope="module")
def voter_token():
    # create voter for test if not exists
    client.post("/voter/login?voter_id=TESTVOTER")  # triggers creation in DB if absent
    res = client.post("/voter/login?voter_id=TESTVOTER")
    assert res.status_code == 200
    return res.json()["token"]


# ------------------------------------------------------
# Missing Token Tests
# ------------------------------------------------------

def test_missing_token_on_admin_route():
    res = client.get("/admin/voters/count")
    assert res.status_code == 401   # unauthorized
    assert "Not authenticated" in res.json()["detail"]


def test_missing_token_on_voter_route():
    res = client.get("/voter/candidates")
    assert res.status_code == 401
    assert "Not authenticated" in res.json()["detail"]


# ------------------------------------------------------
# Invalid Token Tests
# ------------------------------------------------------

def test_invalid_token_rejected_admin_route():
    res = client.get(
        "/admin/voters/count",
        headers={"Authorization": "FAKE_TOKEN"}
    )
    assert res.status_code in (401, 403)


def test_invalid_token_rejected_voter_route():
    res = client.get(
        "/voter/candidates",
        headers={"Authorization": "FAKE_TOKEN"}
    )
    assert res.status_code in (401, 403)


# ------------------------------------------------------
# Cross-Permission Tests (Voter → Admin)
# ------------------------------------------------------

def test_voter_cannot_access_admin_routes(voter_token):
    res = client.get(
        "/admin/voters/count",
        headers={"Authorization": voter_token}
    )
    assert res.status_code == 403
    assert "Admin access required" in res.json()["detail"]


def test_voter_cannot_modify_candidates(voter_token):
    res = client.post(
        "/admin/candidate/add?name=ILLEGAL",
        headers={"Authorization": voter_token}
    )
    assert res.status_code == 403


# ------------------------------------------------------
# Cross-Permission Tests (Admin → Voter)
# ------------------------------------------------------

def test_admin_cannot_access_voter_specific_routes(admin_token):
    res = client.get(
        "/voter/candidates",
        headers={"Authorization": admin_token}
    )
    assert res.status_code == 403
    assert "Voter access required" in res.json()["detail"]


def test_admin_cannot_cast_vote(admin_token):
    res = client.post(
        "/voter/vote/1",
        headers={"Authorization": admin_token}
    )
    assert res.status_code == 403


# ------------------------------------------------------
# Authorized Access Tests
# ------------------------------------------------------

def test_admin_access_allowed(admin_token):
    res = client.get(
        "/admin/voters/count",
        headers={"Authorization": admin_token}
    )
    assert res.status_code == 200


def test_voter_access_allowed(voter_token):
    res = client.get(
        "/voter/candidates",
        headers={"Authorization": voter_token}
    )
    assert res.status_code == 200
