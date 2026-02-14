#!/usr/bin/env bash
# Deploy lacuene site to production (LXC 612 via tulip)
set -euo pipefail

SITE_DIR="$(cd "$(dirname "$0")" && pwd)/output/site"
TULIP="root@172.20.1.10"

# Verify site files exist
if [[ ! -f "$SITE_DIR/index.html" ]]; then
    echo "ERROR: $SITE_DIR/index.html not found. Run 'just site' first."
    exit 1
fi

echo "lacuene site ready at: $SITE_DIR"
echo "  index.html: $(du -h "$SITE_DIR/index.html" | cut -f1)"
echo "  about.html: $(du -h "$SITE_DIR/about.html" | cut -f1)"
echo ""

case "${1:-}" in
    --prod)
        echo "Deploying to LXC 612 (lacuene.apercue.ca)..."
        for f in index.html about.html; do
            scp "$SITE_DIR/$f" "$TULIP:/tmp/lacuene-$f"
            ssh "$TULIP" "pct push 612 /tmp/lacuene-$f /var/www/lacuene.apercue.ca/$f"
        done
        echo "Deployed to https://lacuene.apercue.ca"
        ;;
    --serve)
        echo "Starting local server at http://localhost:8000"
        python3 -m http.server 8000 -d "$SITE_DIR"
        ;;
    *)
        echo "Usage:"
        echo "  deploy.sh --prod    Deploy to LXC 612 (lacuene.apercue.ca)"
        echo "  deploy.sh --serve   Start local preview server"
        ;;
esac
