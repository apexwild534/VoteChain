#!/bin/bash

echo "=========================================="
echo "        VoteChain Startup Script"
echo "=========================================="

# Stop on error
set -e

# ------------------------------------------
# 1. Activate Virtual Environment
# ------------------------------------------

if [ -d "venv" ]; then
    echo "[*] Activating virtual environment..."
    source venv/bin/activate
else
    echo "[!] No venv found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "[*] Installing dependencies..."
    pip install --upgrade pip
    pip install fastapi uvicorn sqlalchemy pydantic jwt
fi

# ------------------------------------------
# 2. Ensure database exists
# ------------------------------------------

echo "[*] Initializing database tables..."
python3 - << 'EOF'
from backend.database.session import Base, engine
Base.metadata.create_all(bind=engine)
print("[+] Database ready.")
EOF

# ------------------------------------------
# 3. Launch the Backend Server
# ------------------------------------------

echo "[*] Starting VoteChain backend..."
echo "------------------------------------------"
echo "Server running at: http://localhost:8000"
echo "API Docs:          http://localhost:8000/docs"
echo "------------------------------------------"

uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
