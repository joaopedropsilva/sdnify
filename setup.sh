#!/usr/bin/bash

PROJECT_ROOT=$(realpath "$(dirname "$0")")

FAUCET_LOG_DIR="$PROJECT_ROOT/var/log/faucet"
echo [setup] Creating faucet log files
mkdir -p $FAUCET_LOG_DIR
files=("faucet.log" "faucet_exception.log" "gauge.log" "gauge_exception.log")

for file in "${files[@]}"; do
    touch "$FAUCET_LOG_DIR/$file"
done
echo [setup] Log files creation finished!

echo [setup] Building test environment docker image
docker build -t sdnify-test-env .
echo [setup] Test environment successfully built!

if [ "$1" == "--local" ]; then
    echo [setup] Installing python dependencies
    $PROJECT_ROOT/etc/install-deps.sh
    echo [setup] Dependencies successfully installled!

    echo [setup] Sourcing functions
    $PROJECT_ROOT/etc/source.sh
fi

