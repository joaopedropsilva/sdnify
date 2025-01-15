#!/usr/bin/bash

PROJECT_ROOT=$(realpath "$(dirname "$0")")

cd $PROJECT_ROOT/
python -m src.cli "$@"
cd - > /dev/null

