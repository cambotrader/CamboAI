#!/bin/bash
# build.sh for Render deployment

# Exit on error
set -e

echo "Starting build process..."

# Install Python dependencies
echo "Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install TA-Lib using pip
echo "Installing TA-Lib using pip..."
pip install TA-Lib

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
