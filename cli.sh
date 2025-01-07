#!/usr/bin/bash

PROJECT_ROOT=$(dirname "$(realpath "$0")")

cd $PROJECT_ROOT/
source $PROJECT_ROOT/src/ovs.sh

#python -m src.cli "$@"

cd - > /dev/null

