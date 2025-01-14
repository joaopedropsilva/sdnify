#!/usr/bin/env bash

PROJECT_ROOT="/root/test"

service openvswitch-switch start
ovs-vsctl set-manager ptcp:6640
$PROJECT_ROOT/create_env.sh
source $PROJECT_ROOT/.venv/bin/activate
bash
service openvswitch-switch stop

