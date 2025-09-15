#!/bin/bash
# build.sh for Render deployment

# Exit on error and print commands
set -ex

# Install Python dependencies
echo "Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install NumPy the easy way (binary wheel)
echo "Installing NumPy binary wheel..."
pip install --only-binary=numpy numpy==1.24.3

# Install TA-Lib using pip (instead of building from source)
echo "Installing TA-Lib using pip..."
pip install TA-Lib

# Install all required packages explicitly
echo "Installing critical dependencies..."
pip install fastapi==0.68.0 uvicorn==0.15.0 prometheus-client sentry-sdk slowapi

# Install backend requirements
echo "Installing backend requirements..."
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt
else
    echo "WARNING: backend/requirements.txt not found!"
    # Try to find requirements.txt in other locations
    find . -name "requirements.txt" -type f
fi

# Install any additional requirements
if [ -f "requirements.txt" ]; then
    echo "Installing root requirements..."
    pip install -r requirements.txt
fi

echo "Build completed successfully!"
