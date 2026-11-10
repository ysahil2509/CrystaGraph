#!/usr/bin/env bash
# ==============================================================================
# CrystaGraph Full-Stack Production Launch Script
# Starts FastAPI Microservice (Port 8000) & Next.js 14 App (Port 3000)
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "======================================================================="
echo "  🔬 CrystaGraph: Materials Informatics & Knowledge Mining Platform"
echo "  BML Munjal University &bull; Dept. of Computer Science & Engineering"
echo "======================================================================="

# Verify Python database exists
if [ ! -f "data/database/matgraph.db" ]; then
    echo "[Init] Initializing SQLite database schema and ingesting benchmark papers..."
    python3 scripts/build_database.py
    python3 scripts/process_papers.py
fi

# Verify ML models
if [ ! -f "models/model_Yield_Strength.joblib" ]; then
    echo "[Init] Training ML property prediction models..."
    python3 models/train_property_predictor.py
fi

# Cleanup on exit
cleanup() {
    echo -e "\n[Shutdown] Stopping CrystaGraph services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    echo "[Shutdown] All services cleanly stopped."
    exit 0
}
trap cleanup SIGINT SIGTERM

# 1. Start FastAPI backend on port 8000
echo "[1/2] Starting FastAPI backend on http://0.0.0.0:8000..."
python3 -m uvicorn app.api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend healthcheck
sleep 2

# 2. Start Next.js frontend on port 3000
echo "[2/2] Starting Next.js frontend on http://0.0.0.0:3000..."
cd frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "======================================================================="
echo "  ✅ CrystaGraph Platform is LIVE!"
echo "  • Web Application:  http://localhost:3000"
echo "  • FastAPI REST API: http://localhost:8000"
echo "  • API Swagger Docs: http://localhost:8000/docs"
echo "  • SQLite Database:  data/database/matgraph.db"
echo "======================================================================="
echo "Press Ctrl+C to stop all services."

wait
