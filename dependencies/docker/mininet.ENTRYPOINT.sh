#!/usr/bin/env bash

DEPENDENCIES_DIR="/root/app/dependencies"

service openvswitch-switch start
ovs-vsctl set-manager ptcp:6640

$DEPENDENCIES_DIR/create_env.sh
bash

service openvswitch-switch stop

