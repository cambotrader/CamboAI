#!/bin/bash
# build.sh for Render deployment

# Exit on error and print commands
set -ex

# Install Python dependencies
echo "Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install NumPy first, using a version known to have binary wheels
echo "Installing NumPy binary wheel..."
pip install numpy==1.22.4 --no-build-isolation

# Install TA-Lib using pip
echo "Installing TA-Lib using pip..."
pip install TA-Lib

# Install all required packages explicitly
echo "Installing critical dependencies..."
pip install fastapi==0.68.0 uvicorn==0.15.0 prometheus-client sentry-sdk slowapi

# Install backend requirements
echo "Installing backend requirements..."
if [ -f "backend/requirements.txt" ]; then
    # Temporarily create a version without numpy (since we already installed it)
    grep -v "numpy" backend/requirements.txt > backend/requirements_without_numpy.txt
    pip install -r backend/requirements_without_numpy.txt
    rm backend/requirements_without_numpy.txt
else
    echo "WARNING: backend/requirements.txt not found!"
    # Try to find requirements.txt in other locations
    find . -name "requirements.txt" -type f
fi

# Install any additional requirements
if [ -f "requirements.txt" ]; then
    echo "Installing root requirements..."
    # Temporarily create a version without numpy (since we already installed it)
    grep -v "numpy" requirements.txt > requirements_without_numpy.txt
    pip install -r requirements_without_numpy.txt
    rm requirements_without_numpy.txt
fi

echo "Build completed successfully!"
