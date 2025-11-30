#!/usr/bin/env bash

# Script to run one or more Agent.py instances for the Cards server.
# Usage: scripts/run_agent.sh [--reuse-venv] [--no-install] [--count N] [--policy POLICY] [--delay D]
# Example:
#   scripts/run_agent.sh --reuse-venv --count 2 --policy random --delay 0.15

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$ROOT_DIR/venv"
PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"
REQS="$ROOT_DIR/requirements.txt"

REUSE_VENV=0
NO_INSTALL=0
COUNT=1
POLICY=greedy
DELAY=0.3

show_help() {
  cat <<EOF
Usage: $0 [options]
Options:
  --reuse-venv        Reuse an existing ./venv if present (default recreates venv)
  --no-install        Skip installing requirements into the venv
  --count N           Start N agents (default 1)
  --policy POLICY     Agent policy to use: 'greedy' or 'random' (default greedy)
  --delay D           Delay between agent polls in seconds (default 0.3)
  -h, --help          Show this help
Examples:
  $0 --reuse-venv --count 2 --policy random --delay 0.2
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reuse-venv)
      REUSE_VENV=1; shift
      ;;
    --no-install)
      NO_INSTALL=1; shift
      ;;
    --count)
      COUNT="$2"; shift 2
      ;;
    --policy)
      POLICY="$2"; shift 2
      ;;
    --delay)
      DELAY="$2"; shift 2
      ;;
    -h|--help)
      show_help; exit 0
      ;;
    *)
      echo "Unknown argument: $1"; show_help; exit 1
      ;;
  esac
done

# Create venv if missing or if not reusing
if [[ $REUSE_VENV -eq 1 && -x "$PYTHON" ]]; then
  echo "Using existing venv at $VENV_DIR"
else
  echo "(Re)creating venv at $VENV_DIR"
  if [[ -d "$VENV_DIR" ]]; then
    rm -rf "$VENV_DIR"
  fi
  python3 -m venv "$VENV_DIR"
fi

if [[ $NO_INSTALL -eq 0 ]]; then
  echo "Installing requirements (may take a moment)"
  "$PIP" install --upgrade pip
  "$PIP" install -r "$REQS"
else
  echo "Skipping dependency installation (--no-install)"
fi

# Ensure we use headless SDL driver so pygame can import in headless/CI envs
export SDL_VIDEODRIVER=${SDL_VIDEODRIVER:-dummy}

# Ensure server is listening at port 5550; if not, warn but continue
if ! ss -ltnp 2>/dev/null | grep -q ":5550\s"; then
  echo "Warning: no process listening on port 5550; make sure the server is running before starting agents."
fi

PIDS=()
for i in $(seq 1 $COUNT); do
  # Launch the agent with optional stagger (small random sleep) so multiple agents don't collide exactly
  STAGGER=$(awk -v min=0.05 -v max=0.25 'BEGIN{srand(); print min + rand()*(max-min)}')
  echo "Starting Agent #$i (policy=$POLICY, delay=$DELAY) after stagger ${STAGGER}s"
  (sleep "$STAGGER" && "$PYTHON" "$ROOT_DIR/Agent.py" --policy "$POLICY" --delay "$DELAY") &
  PIDS+=("$!")
done

echo "Started ${#PIDS[@]} agent(s) with PIDs: ${PIDS[*]}"

# Print an easy-to-use line to kill these if needed
echo "To stop these agents, run: kill ${PIDS[*]}"

exit 0
