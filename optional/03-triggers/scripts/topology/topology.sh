#!/bin/bash
# topology — Device mesh awareness CLI
# Installed to ~/.local/bin/topology by install.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/topology/topology.py" "$@"