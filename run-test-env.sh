#!/usr/bin/env bash

PROJECT_ROOT=$(realpath "$(dirname "$0")")

docker container rm -f sdnify-test-env > /dev/null
docker run --tty --interactive --privileged --name sdnify-test-env \
    --volume $PROJECT_ROOT:/root/test \
    --network=sdnify_default \
    sdnify-test-env

