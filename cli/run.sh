#!/bin/bash

echo "Starting python service..."
./.venv/bin/python ./src/main.py &
PYTHON_PID=$!

echo "Starting go service..."
./dist/fileserver

echo "Go service exited. Shutting down Python (PID: $PYTHON_PID)..."
kill $PYTHON_PID
wait $PYTHON_PID 2>/dev/null

echo "Shutdown complete."