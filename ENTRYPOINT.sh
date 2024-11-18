#!/usr/bin/env bash

service openvswitch-switch start
ovs-vsctl set-manager ptcp:6640

./create_env.sh
bash

service openvswitch-switch stop

