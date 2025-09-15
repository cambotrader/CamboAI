#!/bin/bash
# Simple build script

# Update pip
pip install --upgrade pip setuptools wheel

# Install NumPy the easy way
pip install --only-binary=numpy numpy==1.24.3

# Install TA-Lib
pip install TA-Lib

# Install all required packages explicitly
pip install fastapi uvicorn prometheus_client

# Install other requirements
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt
fi

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi
