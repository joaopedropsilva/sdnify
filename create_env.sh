#!/usr/bin/env bash

PROJECT_ROOT=$(dirname "$(realpath "$0")")

echo [create_env] Creating python venv
rm -rf "$PROJECT_ROOT/.venv"
python3 -m venv "$PROJECT_ROOT/.venv"
source "$PROJECT_ROOT/.venv/bin/activate"
python3 -m pip install -r "$PROJECT_ROOT/requirements.txt"
echo [create_env] Virtual env created successfully!

