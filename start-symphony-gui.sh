#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_dir"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js was not found on PATH. Install Node.js 20+ and run this again." >&2
  exit 1
fi

echo "Starting SpriteMake Mini-Symphony GUI..."
echo "A free local port will be selected automatically."
echo "Live log: output/SYMPHONY-GUI.log"
echo

exec node tools/symphony-gui/server.js
