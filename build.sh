#!/bin/bash
# build.sh for Render deployment

# Exit on error and print commands
set -ex

# Install system dependencies
apt-get update
apt-get install -y build-essential wget curl libc6-dev

# Download and install TA-Lib
echo "Downloading TA-Lib..."
wget -q http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
echo "Extracting TA-Lib..."
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
echo "Configuring TA-Lib..."
./configure --prefix=/usr
echo "Building TA-Lib..."
make
echo "Installing TA-Lib..."
make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Install Python dependencies
echo "Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

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
