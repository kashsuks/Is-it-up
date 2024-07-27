#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Check the OS type and activate the virtual environment
if [[ "$OSTYPE" == "darwin"* ]]; then
    source venv/bin/activate
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    source venv/bin/activate
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    echo "Unknown OS"
    exit 1
fi

# Install the requirements
pip install -r requirements.txt

# Run the main Python script
python main.py
