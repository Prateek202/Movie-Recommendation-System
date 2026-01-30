#!/bin/bash
set -e

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Generating pickle files..."
python create_pickle.py

echo "Build complete!"
