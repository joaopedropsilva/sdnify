#!/usr/bin/bash

PROJECT_ROOT=$(dirname "$(realpath "$0")")

FAUCET_LOG_DIR="$PROJECT_ROOT/var/log/faucet"
echo [setup] Creating faucet log files
mkdir -p $FAUCET_LOG_DIR
files=("faucet.log" "faucet_exception.log" "gauge.log" "gauge_exception.log")

for file in "${files[@]}"; do
    touch "$FAUCET_LOG_DIR/$file"
done
echo [setup] Log files creation finished!

LIB_DIR="$PROJECT_ROOT/var/lib"
echo [setup] Creating lib dirs
mkdir -p $LIB_DIR/{prometheus,grafana}
echo [setup] Lib dirs creation finished!

