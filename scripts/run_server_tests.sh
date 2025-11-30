#!/usr/bin/env bash

# Run server integration tests for the Cards project.
# Usage: scripts/run_server_tests.sh [--reuse-venv | --no-install] [pytest-args]
# By default this script creates/uses ./venv and installs requirements from requirements.txt.
# It also sets SDL_VIDEODRIVER=dummy for headless environments.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$ROOT_DIR/venv"
PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"
REQUIREMENTS="$ROOT_DIR/requirements.txt"

REUSE_VENV=0
NO_INSTALL=0
PYTEST_ARGS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reuse-venv)
      REUSE_VENV=1
      shift
      ;;
    --no-install)
      NO_INSTALL=1
      shift
      ;;
    --)
      shift; break
      ;;
    -*)
      PYTEST_ARGS+="$1 "; shift
      ;;
    *)
      PYTEST_ARGS+="$1 "; shift
      ;;
  esac
done

echo "Running integration tests for Cards (server)"

# Ensure virtualenv exists (or create it) unless we are told to not reuse.
if [[ $REUSE_VENV -eq 1 && -x "$PYTHON" ]]; then
  echo "Using existing venv at $VENV_DIR"
else
  echo "Creating virtual environment at $VENV_DIR"
  if [[ -d "$VENV_DIR" ]]; then
    rm -rf "$VENV_DIR"
  fi
  python3 -m venv "$VENV_DIR"
fi

# Install requirements if requested
if [[ $NO_INSTALL -eq 0 ]]; then
  echo "Installing requirements from $REQUIREMENTS into venv"
  "$PIP" install --upgrade pip
  "$PIP" install -r "$REQUIREMENTS"
else
  echo "Skipping dependency installation (--no-install)"
fi

# Export SDL_VIDEODRIVER so pygame can run headless
export SDL_VIDEODRIVER=${SDL_VIDEODRIVER:-dummy}

# Run pytest - only server tests by default
TEST_PATTERN="tests/test_server_integration.py"

echo "Running pytest on $TEST_PATTERN with args: $PYTEST_ARGS"

# Activate venv tooling via python -m pytest to avoid sourcing activation
set -x
"$PYTHON" -m pytest -q $TEST_PATTERN $PYTEST_ARGS

EXIT_CODE=$?
set +x

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "Tests failed (exit=$EXIT_CODE)"
  exit $EXIT_CODE
fi

echo "Integration tests passed"
exit 0
