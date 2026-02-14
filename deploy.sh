#!/usr/bin/env bash
# Deploy froq site
set -euo pipefail

SITE_DIR="$(cd "$(dirname "$0")" && pwd)/output/site"

# Verify site files exist
if [[ ! -f "$SITE_DIR/index.html" ]]; then
    echo "ERROR: $SITE_DIR/index.html not found. Run 'just site' first."
    exit 1
fi

echo "Deploying froq..."
echo "  Source: $SITE_DIR"

# TODO: Configure deployment target
echo "ERROR: No deployment target configured. Edit deploy.sh to add your hosting details."
exit 1
