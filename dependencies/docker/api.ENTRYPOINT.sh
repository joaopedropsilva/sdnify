#!/usr/bin/env bash

PROJECT_DIR='/root/app'
DEPENDENCIES_DIR="$PROJECT_DIR/dependencies"

$DEPENDENCIES_DIR/create_env.sh

source $PROJECT_DIR/.venv/bin/activate

python -m src.api

