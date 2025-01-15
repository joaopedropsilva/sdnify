#!/usr/bin/env bash

PROJECT_ROOT=$(realpath "$(dirname "$(dirname "$0")")")

docker container rm -f sdnify-test-env
docker run --tty --interactive --privileged --name sdnify-test-env \
    -v $PROJECT_ROOT/etc/faucet/faucet.yaml:/root/test/etc/faucet/faucet.yaml \
    sdnify-test-env

