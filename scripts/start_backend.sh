#!/bin/bash
# Quick start script for Visual Block Runtime

set -e

echo "=== Visual Block Runtime - Quick Start ==="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required"
    exit 1
fi

# Start backend
echo "Starting backend..."
cd backend
python3 main.py &
BACKEND_PID=$!

# Wait for backend
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo "Backend is ready!"
        break
    fi
    sleep 0.5
done

# Check if backend is ready
if ! curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "Error: Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "=== Backend is running on http://127.0.0.1:8000 ==="
echo ""
echo "To start the frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "Press Ctrl+C to stop the backend"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID 2>/dev/null; exit" INT
wait
