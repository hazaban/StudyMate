#!/bin/bash
set -e

echo "=== StudyMate Frontend Build ==="
echo "Node version: $(node --version)"
echo "npm version: $(npm --version)"

npm ci
npm run build:h5

echo "=== Build completed ==="