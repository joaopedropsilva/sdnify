#!/usr/bin/env bash

DEPENDENCIES_DIR=$(dirname "$(realpath "$0")")
PROJECT_ROOT=$(dirname "$DEPENDENCIES_DIR")

echo [create_env] Criando ambiente virtual python

rm -rf "$PROJECT_ROOT/.venv"

python3 -m venv "$PROJECT_ROOT/.venv"
source "$PROJECT_ROOT/.venv/bin/activate"
python3 -m pip install -r "$DEPENDENCIES_DIR/requirements.txt"

echo [create_env] Ambiente criado com sucesso!
