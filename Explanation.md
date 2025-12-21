# 📘 Explanation.md  
## VoteChain – Blockchain-Backed Secure Voting System

---

## 1. Introduction

**VoteChain** is a secure electronic voting system that combines a **traditional database** with a **custom blockchain layer** to ensure vote integrity, transparency, and immutability.

Unlike conventional voting systems where votes are stored directly in databases (and can theoretically be altered), VoteChain **stores votes as blockchain transactions**, making tampering practically impossible once votes are sealed into blocks.

The project is designed for:
- academic demonstration
- understanding blockchain fundamentals
- learning secure backend system design

---

## 2. Problem Statement

Traditional online voting systems face several challenges:

1. Votes stored in databases can be modified by administrators.
2. Voter anonymity is hard to guarantee.
3. Election results depend entirely on database trust.
4. Double voting must be strictly prevented.
5. Transparency and auditability are limited.

---

## 3. Solution Overview

VoteChain addresses these problems by introducing:

- **JWT-based authentication** for voters and administrators
- **Role-based access control**
- **Blockchain-based vote storage**
- **Database usage only for identity and state**
- **Result computation from blockchain, not database**

This hybrid design ensures:
- performance of databases
- security of blockchains
- clarity of system responsibilities

---

## 4. High-Level Architecture

```

Client (Swagger / API)
↓
FastAPI Application
↓
┌──────────────────────────┐
│ Authentication (JWT)     │
│ Admin Routes             │
│ Voter Routes             │
└───────────┬──────────────┘
│
┌──────────▼──────────┐     ┌──────────────────────┐
│ SQLite Database     │     │ Blockchain Layer     │
│ (Users & State)    │◄───►│ (Votes & Integrity)  │
└────────────────────┘     └──────────────────────┘

````

---

## 5. Technology Stack

| Component | Technology |
|--------|-----------|
| Backend Framework | FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy |
| Authentication | JWT (PyJWT) |
| Blockchain | Custom Python Implementation |
| API Docs | Swagger (OpenAPI) |

---

## 6. Database Design

### 6.1 Purpose of Database

The database is **not used to store votes**.

It stores:
- voter identities
- candidate details
- election state
- voting status (has voted / not)

---

### 6.2 Tables

#### 6.2.1 Voters Table
```text
voters
-------------------------
id (PK)
voter_id (unique)
voter_hash (unique)
has_voted (boolean)
````

* `voter_id` → login identity
* `voter_hash` → anonymized blockchain identifier
* `has_voted` → prevents double voting

---

#### 6.2.2 Candidates Table

```text
candidates
-------------------------
id (PK)
name
```

---

#### 6.2.3 Election State Table

```text
election_state
-------------------------
id (PK)
status (NOT_STARTED | ONGOING | ENDED)
```

Only **one row exists** at any time.

---

## 7. Blockchain Design

### 7.1 Why Blockchain?

Blockchain provides:

* immutability
* tamper resistance
* auditability
* chronological ordering of votes

Once votes are added to a block, they **cannot be altered without breaking the chain**.

---

### 7.2 Blockchain Components

#### 7.2.1 Transaction (VoteTransaction)

Each vote is represented as a transaction:

```text
VoteTransaction
-------------------------
voter_hash
candidate_id
timestamp
```

* Voter identity is **hashed (SHA-256)** for anonymity.
* No personal data is stored in the blockchain.

---

#### 7.2.2 Block

```text
Block
-------------------------
index
timestamp
transactions[]
previous_hash
hash
```

Each block links to the previous block using `previous_hash`.

---

#### 7.2.3 Chain

```text
[ Genesis Block ]
        ↓
[ Block 1 ]
        ↓
[ Block 2 ]
```

Votes are added as **pending transactions** and mined only when the election ends.

---

## 8. Consensus Model

VoteChain uses a **trusted local consensus model**, not Proof-of-Work or Proof-of-Stake.

Reasons:

* academic clarity
* single-node deployment
* no energy waste
* deterministic behavior

Consensus responsibilities:

* validate chain integrity
* resolve forks (if applicable)
* ensure hash correctness

---

## 9. Authentication & Authorization

### 9.1 JWT Authentication

* JSON Web Tokens (JWT) are used
* Tokens contain:

  * subject (`sub`)
  * role (`admin` or `voter`)
  * issue time

---

### 9.2 Roles

| Role  | Capabilities              |
| ----- | ------------------------- |
| Admin | Manage election lifecycle |
| Voter | Vote once, view results   |

---

### 9.3 Access Enforcement

* Admin routes → admin token required
* Voter routes → voter token required
* Role mismatch → HTTP 403 Forbidden

---

## 10. Application Flow

### 10.1 Admin Flow

```
Login
  ↓
Add Candidates
  ↓
Start Election
  ↓
End Election
  ↓
View Results
```

---

### 10.2 Voter Flow

```
Register
  ↓
Login
  ↓
View Candidates
  ↓
Vote (once)
  ↓
View Results
```

---

## 11. Vote Casting Process (Detailed)

1. Voter logs in → receives JWT
2. Voter selects candidate
3. System checks:

   * election status
   * voter existence
   * double voting
4. Vote is:

   * hashed
   * added as blockchain transaction
5. Voter is marked as `has_voted`

Votes are **not counted yet**.

---

## 12. Election Finalization

When admin ends the election:

1. Pending transactions are mined into a block
2. Block hash is calculated
3. Block is appended to the chain
4. Election state becomes `ENDED`

After this point:

* votes cannot be changed
* results become available

---

## 13. Result Calculation

Results are computed by:

1. Iterating through blockchain blocks
2. Counting candidate IDs
3. Calculating:

   * total votes
   * percentages
   * voter turnout

The database is **never used to count votes**.

---

## 14. Security Measures

* Voter anonymity via hashing
* Double voting prevention
* Immutable blockchain storage
* Role-based authorization
* No vote-identity mapping stored

---

## 15. Limitations

* Single-node blockchain
* No distributed consensus
* JWT passed via query parameters (local setup)
* No encryption at rest
* Not production-grade (by design)

---

## 16. Future Enhancements

* Distributed blockchain nodes
* Persistent blockchain storage
* Merkle tree validation
* HTTPS & header-based auth
* UI frontend
* Mobile support

---

## 17. Learning Outcomes

This project demonstrates:

* backend system architecture
* blockchain fundamentals
* secure API design
* database + blockchain hybrid systems
* real-world debugging
* authentication workflows

---

## 18. Conclusion

VoteChain successfully shows how **blockchain technology can be integrated into real-world applications** to solve trust and integrity problems.

By separating identity storage (database) from vote storage (blockchain), the system achieves both efficiency and security.
