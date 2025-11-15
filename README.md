
# VoteChain  
A Local-Network, Blockchain-Backed Voting System

VoteChain is a lightweight, secure voting platform designed for controlled environments such as classrooms, labs, and local networks.  
It provides a blockchain-based audit trail to ensure vote immutability and offers clear separation between administrator and voter functionalities.

This repository contains backend services, frontend interfaces, blockchain logic, and testing tools.

For detailed system behavior and deeper explanations, see **[Explanation.md](Explanation.md)**.  
For usage rights and distribution terms, see **[LICENSE](License)**.

---

## Overview

VoteChain consists of:
- A FastAPI backend for election logic, authentication, and blockchain operations.
- A custom blockchain implementation that stores vote transactions.
- A simple HTML/JS frontend for both administrators and voters.
- A set of scripts for resetting elections, generating demo data, and development.
- A full test suite covering authentication, blockchain, permissions, and voting flow.

---

# System Architecture Diagram
```
                     ┌──────────────────────────────────┐
                     │             Frontend             │
                     │  (HTML / JS, runs in browser)    │
                     ├──────────────────────────────────┤
                     │ Admin UI         │    Voter UI   │
                     │ index.html       │  login.html   │
                     │ manage_candidates│  vote.html    │
                     │ results.html     │  results.html │
                     └───────────▲──────┴──────▲────────┘
                                 │             │
                                 ▼             ▼
                     ┌──────────────────────────────────┐
                     │           FastAPI Backend        │
                     ├──────────────────────────────────┤
                     │ Authentication Routes            │
                     │ Admin Routes                     │
                     │ Voter Routes                     │
                     │ Election State Machine           │
                     └───────────▲──────────────────────┘
                                 │
                                 ▼
                     ┌──────────────────────────────────┐
                     │        Blockchain Engine         │
                     ├──────────────────────────────────┤
                     │ Block Creation                   │
                     │ Vote Transactions                │
                     │ Hash Linking (SHA-256)           │
                     │ Chain Validation                 │
                     │ Optional Persistence             │
                     └───────────▲──────────────────────┘
                                 │
                                 ▼
                     ┌──────────────────────────────────┐
                     │           SQLite Database        │
                     ├──────────────────────────────────┤
                     │ Voters Table                     │
                     │ Candidates Table                 │
                     │ Election State Table             │
                     └──────────────────────────────────┘

```

---

# Blockchain Flow Diagram

```

+------------------+
| Voter Casts Vote |
+--------+---------+
|
v
+--------------------------+
| VoteTransaction(v → c)  |
+--------------------------+
|
v
+--------------------------+
| Added to mempool        |
| (current_transactions)   |
+--------------------------+
|
v
+--------------------------+
|    Block Mined           |
+--------------------------+
| index                    |
| timestamp                |
| transactions (votes)     |
| previous_hash            |
| hash                     |
+--------------------------+
|
v
+--------------------------+
|     Appended to Chain    |
+--------------------------+

```

---

# Directory Structure

```

Votechain/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── routes/
│   ├── database/
│   ├── blockchain/
│   ├── security/
│   ├── utils/
│   ├── scripts/
│   └── tests/
│
├── frontend/
│   ├── admin/
│   ├── voter/
│   ├── components/
│   └── static/
│
├── startup.sh
├── run.sh
├── requirements.txt
├── README.md
├── [Explanation.md](Explanation.md)
└── [LICENSE](License)

````

For detailed explanations of architectural decisions, refer to **[Explanation.md](Explanation.md)**.

---

# Installation

### 1. Clone Repository

```bash
git clone https://github.com/user/VoteChain.git
cd VoteChain
````

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Backend

```bash
./startup.sh
```

Subsequent runs:

```bash
./run.sh
```

Backend available at:

```
http://localhost:8000
```

API documentation:

```
http://localhost:8000/docs
```

---

# Working with Scripts

### Generate Test Data

```bash
python -m backend.scripts.generate_test_data
```

### Reset Blockchain + Election

```bash
python -m backend.scripts.reset_chain
```

---

# Running Tests

```bash
pytest backend/tests -v
```

Includes:

* Authentication tests
* Permission enforcement
* Blockchain integrity tests
* Full voting workflow tests

---

# API Summary

### Authentication

```
POST /admin/login
POST /voter/login
```

### Admin

```
POST /admin/election/start
POST /admin/election/end
GET  /admin/results
GET  /admin/voters
POST /admin/candidate/add
PUT  /admin/candidate/update/{id}
DELETE /admin/candidate/delete/{id}
GET  /admin/blockchain
```

### Voter

```
GET  /voter/candidates
POST /voter/vote/{candidate_id}
GET  /voter/results
```

### Public

```
GET /election/status
```

---

# LICENSE

This project is distributed under the terms of the **[LICENSE](License)** file included in the repository.

---

# Documentation

For a full breakdown of the blockchain, election lifecycle, authentication logic, and system decisions, see:

**[Explanation.md](Explanation.md)**

