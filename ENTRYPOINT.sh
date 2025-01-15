#!/usr/bin/bash

PROJECT_ROOT="/root/test"

service openvswitch-switch start
ovs-vsctl set-manager ptcp:6640
$PROJECT_ROOT/etc/install-deps.sh
bash
service openvswitch-switch stop

