#!/bin/bash
# POSIX shell wrapper for fetch_offline_archives.py
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIER="${1:-simple}"

python3 "$SCRIPT_DIR/fetch_offline_archives.py" --tier "$TIER"
