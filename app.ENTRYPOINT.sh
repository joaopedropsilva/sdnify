#!/usr/bin/env bash

PROJECT_ROOT="/root/app"

service openvswitch-switch start
ovs-vsctl set-manager ptcp:6640

$PROJECT_ROOT/create_env.sh
source $PROJECT_ROOT/.venv/bin/activate

python -m src.app

service openvswitch-switch stop

