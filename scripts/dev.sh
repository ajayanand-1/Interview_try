#!/usr/bin/env bash
set -e

# Project Rosetta / Prompt Wars Local Development Launcher
echo "========================================================"
echo " Starting Prompt Wars Multi-Agent Hiring Platform"
echo "========================================================"

# Trap SIGINT to clean up child processes on exit
trap 'kill $(jobs -p) 2>/dev/null' EXIT

# 1. Start FastAPI Backend
echo "-> Starting FastAPI Backend on http://127.0.0.1:8000..."
./.venv/bin/uvicorn src.api.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# 2. Wait for backend health
sleep 1

# 3. Start React Frontend
echo "-> Starting React Frontend on http://localhost:3000..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "PROMPT WARS is ready:"
echo "  Frontend UI: http://localhost:3000"
echo "  Backend API: http://127.0.0.1:8000 (Swagger docs: http://127.0.0.1:8000/docs)"
echo "Press Ctrl+C to stop all servers."
echo ""

wait
