# **Explanation.md**

# VoteChain – Technical Explanation

This document provides a detailed explanation of the architecture, components, and internal logic behind VoteChain.  
It supplements the main `README.md` with deeper technical insights useful for developers, auditors, and reviewers.

---

# 1. System Overview

VoteChain is a local-network voting platform that uses a custom blockchain to ensure vote integrity.  
The platform has two primary roles:

- **Administrator**: manages the election and candidates, views results, resets the chain.
- **Voter**: authenticates using a voter ID and can vote once per election.

The system guarantees:

- One-person-one-vote enforcement
- Tamper-proof voting record storage
- Clear election lifecycle management
- Role-based access control
- Frontend independence via REST API

---

# 2. Backend Architecture

VoteChain’s backend uses **FastAPI** and is divided into the following layers:

```

backend/
├── routes/
├── database/
├── blockchain/
├── security/
├── utils/
└── config.py

```

### 2.1 `routes/`
Contains all API endpoints:
- `admin_routes.py` – candidate management, viewing voters, results, blockchain access
- `voter_routes.py` – voter candidate list, voting, results
- `auth.py` – admin & voter login
- `election.py` – start/end election, status

Each route file is protected by role-specific dependency functions (`require_admin`, `require_voter`).

---

# 3. Database Layer

The database uses **SQLite** (via SQLAlchemy).

### 3.1 Tables

**Voter**
- `id`
- `voter_id`
- `has_voted` (boolean)

**Candidate**
- `id`
- `name`
- `vote_count` (optional; blockchain source of truth is preferred)

**ElectionState**
- `status` → NOT_STARTED / ONGOING / ENDED

### 3.2 CRUD Layer

`backend/database/crud.py` contains wrappers around database operations:
- Adding voters
- Adding/editing/removing candidates
- Fetching lists
- Resetting state

CRUD functions ensure DB logic stays separated from API logic.

---

# 4. Authentication & Authorization

Authentication uses **JWT tokens** generated in `security/tokens.py`.

### 4.1 Login Process

**Admin Login**
- Sends `/admin/login?password=...`
- If correct, receives `token` with `"role": "admin"`

**Voter Login**
- Sends `/voter/login?voter_id=...`
- If voter exists, receives `token` with `"role": "voter"`

### 4.2 Permission Dependencies

Located in `security/permissions.py`:

- `require_admin` → Checks valid token AND role `admin`
- `require_voter` → Checks valid token AND role `voter`

Unauthorized requests return 401/403.

---

# 5. Election Lifecycle

The election is managed by state transitions in the `ElectionState` table.

### Lifecycle Stages

1. **NOT_STARTED**
   - Voters can only view candidates
   - Voting is disabled

2. **ONGOING**
   - Voters can vote once
   - Blockchain is actively receiving transactions

3. **ENDED**
   - Voting disabled
   - Results visible to vote

Transition is controlled through:
```

POST /admin/election/start
POST /admin/election/end

```

---

# 6. Blockchain Design

VoteChain implements a **minimal, educational blockchain**.

### 6.1 Block Structure

Defined in `blockchain/block.py`:

```

index
timestamp
transactions (list of VoteTransaction)
previous_hash
nonce
hash

```

### 6.2 Vote Transactions

Defined in `transaction.py`:

```

voter_hash  (hash(voter_id))
candidate_id
timestamp

```

Voter IDs are hashed to preserve anonymity.

### 6.3 Mining

Implementing a simplified proof-of-work or immediate block creation based on your chain version.

Steps:
1. Pending transactions stored in `current_transactions`
2. When mining:
   - A new block is created
   - All pending transactions assigned to it
   - Block is hashed
   - Added to chain

### 6.4 Chain Validation

`Blockchain.is_chain_valid()` verifies:
- Every block’s hash matches recomputed hash
- `previous_hash` links correctly
- No transaction tampering

### 6.5 Consensus

`consensus.py` implements the **longest valid chain rule**:
- Used if multiple blockchain instances exist on a LAN
- Chain with most valid blocks replaces the shorter one

---

# 7. Frontend Architecture

The frontend uses **plain HTML, CSS, and JavaScript** served statically.

```

frontend/
├── admin/
├── voter/
├── components/
└── static/

```

### Admin UI
- Dashboard
- Manage candidates
- View voters
- View blockchain
- View results
- Clear/reset election

### Voter UI
- Login
- Candidate list
- Vote page
- Results page

Pages use simple `fetch()` calls to interact with the API.

---

# 8. Election Reset & Development Utilities

Scripts in `backend/scripts/`:

### `generate_test_data.py`
Creates demo voters and candidates.

### `reset_chain.py`
Resets:
- election status → NOT_STARTED  
- voter voting flags  
- blockchain → genesis block  
- chain persistence file  

### `startup.sh` / `run.sh`
Local development startup.

---

# 9. Testing Strategy

All tests live in `backend/tests/`.

### 9.1 Authentication Tests
- Valid admin login
- Valid voter login
- Invalid credentials
- Token validation

### 9.2 Permission Tests
- Voter blocked from admin routes
- Admin blocked from voter-only routes
- Missing token behavior

### 9.3 Blockchain Tests
- Genesis block
- Block mining
- Hash validity
- Chain validation
- Tamper detection
- Consensus selection

### 9.4 Full Voting Flow
End-to-end test covering:
1. Start election
2. Login voter
3. Cast vote
4. Double-vote prevention
5. Blockchain growth
6. End election
7. Results availability

---

# 10. Security Considerations

VoteChain is designed for local use and educational settings.  
Security model:

- Role-based JWT authorization
- One-vote-per-person enforced at server level
- Voter anonymity preserved via hashed voter IDs on blockchain
- Blockchain protects vote integrity
- Admin cannot cast votes
- Voter cannot manage election or candidates

For production environments:
- Store secrets in environment variables
- Use HTTPS
- Move admin password to hashed storage

---

# 11. Limitations

VoteChain is intentionally simple.  
It does not include:

- Networked blockchain node propagation
- Byzantine fault tolerance
- Advanced consensus (PoS, Raft, PBFT)
- Distributed storage
- Encrypted votes

It is built for clarity, auditability, and instruction, not real-world elections.


