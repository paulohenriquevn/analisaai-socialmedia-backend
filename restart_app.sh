#!/bin/bash
# Restart the Flask application
echo "Stopping current Flask application..."
pkill -f "python run.py" || echo "No running Flask application found"

# Wait a moment
sleep 2

# Start Flask app in background
echo "Starting Flask application..."
cd "$(dirname "$0")"
python3 run.py > logs/flask.log 2>&1 &

# Wait for startup
sleep 2
echo "Flask application restarted."
