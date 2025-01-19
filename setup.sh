#!/usr/bin/bash

PROJECT_ROOT=$(realpath "$(dirname "$0")")

echo [setup] Deleting docker-compose obsolete volumes
docker compose down
docker volume rm -f sdnify_grafana-storage
docker volume rm -f sdnify_prometheus-storage
echo [setup] Deletion complete!

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

