#!/usr/bin/bash

PROJECT_ROOT=$(dirname "$(realpath "$0")")

cd $PROJECT_ROOT/
python -m src.cli "$@"
cd - > /dev/null

