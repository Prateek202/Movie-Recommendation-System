#!/bin/bash
# Script to create a GitHub release with pickle files

REPO="Prateek202/Movie-Recommendation-System"
TAG="v1.0"
FILES="movies.pkl similarity.pkl"

echo "Creating GitHub release $TAG..."

# Use GitHub CLI if available
if command -v gh &> /dev/null; then
    echo "Using GitHub CLI..."
    gh release create $TAG $FILES --title "Pre-generated Pickle Files" --notes "Pre-generated similarity and movies pickle files for deployment"
    echo "✓ Release created successfully"
else
    echo "GitHub CLI not found. Please use web interface:"
    echo "1. Go to: https://github.com/$REPO/releases/new"
    echo "2. Create tag: $TAG"
    echo "3. Upload files: $FILES"
fi
