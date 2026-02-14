#!/usr/bin/env bash
# Deploy lacuene site locally or via GitHub Pages
set -euo pipefail

SITE_DIR="$(cd "$(dirname "$0")" && pwd)/output/site"

# Verify site files exist
if [[ ! -f "$SITE_DIR/index.html" ]]; then
    echo "ERROR: $SITE_DIR/index.html not found. Run 'just site' first."
    exit 1
fi

echo "lacuene site ready at: $SITE_DIR"
echo "  index.html: $(du -h "$SITE_DIR/index.html" | cut -f1)"
echo "  about.html: $(du -h "$SITE_DIR/about.html" | cut -f1)"
echo ""
echo "Deployment options:"
echo "  1. GitHub Pages (automatic): push to main branch"
echo "     GitHub Actions will build and deploy to GitHub Pages."
echo ""
echo "  2. Local preview:"
echo "     python3 -m http.server 8000 -d $SITE_DIR"
echo ""

# If --serve flag passed, start local server
if [[ "${1:-}" == "--serve" ]]; then
    echo "Starting local server at http://localhost:8000"
    python3 -m http.server 8000 -d "$SITE_DIR"
fi
