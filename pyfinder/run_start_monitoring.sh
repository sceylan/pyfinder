#!/bin/bash

# Usage: ./run_monitor.sh [python_version]
# Default Python version is 3.9 if not specified

PYTHON_VERSION=${1:-3.9}

# Run the script with specified Python version
python$PYTHON_VERSION start_monitoring.py > /dev/null 2>&1 &

# Detach from terminal
disown