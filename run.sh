#!/bin/bash
# Activate Python 3.13 virtual environment and run commands

# Activate virtual environment
source venv/bin/activate

# Run the command passed as arguments
"$@"
