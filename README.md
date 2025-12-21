# 🗳️ VoteChain  
*A Blockchain-Backed Secure Voting System*

---

## 📌 Overview

**VoteChain** is a local-network, blockchain-backed voting platform built using **FastAPI**, **SQLite**, and a **custom lightweight blockchain**.

The system ensures:
- **One person, one vote**
- **Vote immutability** via blockchain
- **Role-based access control** (Admin / Voter)
- **Transparent and verifiable election results**

Votes are **not counted directly from the database**.  
Instead, votes are sealed into blockchain blocks and results are computed **from the blockchain**, ensuring integrity.

---

## 🧠 Core Concepts

- **Database** → stores voters, candidates, and election state  
- **Blockchain** → stores immutable vote transactions  
- **JWT Authentication** → enforces role-based access  
- **FastAPI** → REST API with interactive Swagger UI  

---

## 🏗️ System Architecture

```

┌──────────────┐
│   Frontend   │ (Swagger / API Clients)
└──────┬───────┘
│ HTTP
┌──────▼───────┐
│  FastAPI App │
│──────────────│
│ Auth (JWT)   │
│ Admin Routes │
│ Voter Routes │
└──────┬───────┘
│
┌─────▼───────┐        ┌─────────────────┐
│   Database  │        │   Blockchain     │
│ (SQLite)    │◄──────►│  (In-Memory)     │
│──────────── │        │─────────────────│
│ voters      │        │ blocks           │
│ candidates  │        │ transactions     │
│ election    │        │ hashes           │
└─────────────┘        └─────────────────┘

```

---

## 🔗 Blockchain Design

- **Genesis Block** created at startup
- **VoteTransaction**
  - `voter_hash` (SHA-256 anonymized)
  - `candidate_id`
- Votes are **queued** during election
- On election end → votes are **mined into a block**
- Blocks are chained using `previous_hash`

```

[ Genesis ]
↓
[ Block 1 ]
(votes)
↓
[ Block 2 ]
(votes)

```

---

## 🔐 Authentication & Roles

| Role   | Permissions |
|------|------------|
| Admin | Manage candidates, start/end election, view results |
| Voter | View candidates, cast vote, view results |

Authentication uses **JWT tokens** passed as query parameters (local trusted setup).

---

## 🗂️ Project Structure

```

VoteChain/
├── backend/
│   ├── app.py
│   ├── routes/
│   │   ├── admin_routes.py
│   │   ├── voter_routes.py
│   │   └── auth.py
│   ├── database/
│   │   ├── models.py
│   │   ├── session.py
│   │   └── crud.py
│   ├── blockchain/
│   │   ├── chain.py
│   │   ├── block.py
│   │   ├── transaction.py
│   │   └── consensus.py
│   └── data/
│       └── votechain.db
│
├── .env
├── README.md
├── Explanation.md
└── LICENSE

````

---

## ⚙️ Environment Configuration (`.env`)

```env
VOTECHAIN_ENV=development
VOTECHAIN_DB=sqlite:///data/votechain.db
VOTECHAIN_SECRET_KEY=supersecretchangeme
VOTECHAIN_ADMIN_PASSWORD=admin123
````

---

## 🚀 How to Run the Project

### 1️⃣ Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2️⃣ Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy PyJWT
```

### 3️⃣ Load Environment Variables

```bash
set -a
source .env
set +a
```

### 4️⃣ Initialize Database

```bash
python3 - << 'EOF'
from backend.database.session import Base, engine
Base.metadata.create_all(bind=engine)
print("Database initialized")
EOF
```

### 5️⃣ Start Server

```bash
uvicorn backend.app:app --reload
```

### 6️⃣ Open Swagger UI

```
http://127.0.0.1:8000/docs
```

---

## 🧪 How to Use the System (End-to-End)

### 🔑 Admin Flow

1. **Login**

```
POST /admin/login?password=admin123
```

2. **Add Candidates**

```
POST /admin/candidate/add?name=Alice
POST /admin/candidate/add?name=Bob
```

3. **Start Election**

```
POST /admin/election/start
```

---

### 👤 Voter Flow

1. **Register**

```
POST /voter/register?voter_id=voter1
```

2. **Login**

```
POST /voter/login?voter_id=voter1
```

3. **View Candidates**

```
GET /voter/candidates?token=JWT_TOKEN
```

4. **Cast Vote**

```
POST /voter/vote/{candidate_id}?token=JWT_TOKEN
```

---

### 🧮 Results

5. **End Election (Admin)**

```
POST /admin/election/end
```

6. **View Results**

```
GET /admin/results
GET /voter/results?token=JWT_TOKEN
```

Results are computed **from blockchain data**, not database rows.

---

## 📊 Election Flow Diagram

```
Admin starts election
        ↓
Voters register & login
        ↓
Voters cast votes
        ↓
Votes added as transactions
        ↓
Admin ends election
        ↓
Votes mined into blockchain
        ↓
Results calculated from blockchain
```

---

## 🛡️ Security Considerations

* Voter identity is **hashed** before blockchain storage
* Database never stores vote-candidate mapping
* Blockchain prevents vote tampering
* Role enforcement via JWT

---

## 📄 Documentation

* 📘 **Detailed Explanation** → [`Explanation.md`](./Explanation.md)
* 📜 **License** → [`LICENSE`](./LICENSE)

---

## 🧠 Educational Value

This project demonstrates:

* REST API design
* Blockchain fundamentals
* Secure authentication
* Database + blockchain hybrid architecture
* Real-world debugging and system integration

---

## 🏁 Final Notes

VoteChain is designed for **academic, local, and experimental use**.
It intentionally avoids heavy consensus mechanisms (PoW/PoS) to remain understandable and lightweight.

---
