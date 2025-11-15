#!/bin/bash

echo "=========================================="
echo "        VoteChain — Run Backend"
echo "=========================================="

# Stop on error
set -e

# ------------------------------------------
# Activate virtual environment
# ------------------------------------------
if [ -d "venv" ]; then
    echo "[*] Activating virtual environment..."
    source venv/bin/activate
else
    echo "[!] No virtual environment found!"
    echo "    Run ./startup.sh first."
    exit 1
fi

# ------------------------------------------
# Start FastAPI server
# ------------------------------------------

echo "[*] Running API Server..."
echo "------------------------------------------"
echo "URL:  http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo "------------------------------------------"

uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
