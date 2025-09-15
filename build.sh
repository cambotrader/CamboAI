#!/bin/bash
# build.sh for Render deployment

# Exit on error
set -e

echo "Starting build process..."

# Install Python dependencies
echo "Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install NumPy using binary wheel (no compilation needed)
echo "Installing NumPy binary wheel..."
pip install --only-binary=numpy numpy

# Install TA-Lib using pip
echo "Installing TA-Lib using pip..."
pip install TA-Lib

echo "Installing backend requirements..."
if [ -f "backend/requirements.txt" ]; then
    # Modify requirements to exclude numpy (we installed it separately)
    grep -v "numpy" backend/requirements.txt > backend/requirements_filtered.txt
    pip install -r backend/requirements_filtered.txt
else
    echo "WARNING: backend/requirements.txt not found!"
    # Try to find requirements.txt in other locations
    find . -name "requirements.txt" -type f
fi

# Install any additional requirements
if [ -f "requirements.txt" ]; then
    echo "Installing root requirements..."
    grep -v "numpy" requirements.txt > requirements_filtered.txt
    pip install -r requirements_filtered.txt
fi

echo "Build completed successfully!"
