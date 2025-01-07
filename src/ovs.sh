create_ns () {
    NAME=$1
    IP=$2
    NETNS=faucet-${NAME}
    ip netns add ${NETNS}
    ip link add dev veth-${NAME} type veth peer name veth0 netns ${NETNS}
    ip link set dev veth-${NAME} up
    exec_on ${NAME} ip link set dev lo up
    [ -n "${IP}" ] && exec_on ${NAME} ip addr add dev veth0 ${IP}
    exec_on ${NAME} ip link set dev veth0 up
}

exec_on () {
    NAME=$1
    NETNS=faucet-${NAME}
    shift
    ip netns exec ${NETNS} $@
}

inter_switch_link () {
    SW_A_NAME=$(echo $1 | cut -d ':' -f 1)
    SW_A_PORT=$(echo $1 | cut -d ':' -f 2)
    SW_B_NAME=$(echo $2 | cut -d ':' -f 1)
    SW_B_PORT=$(echo $2 | cut -d ':' -f 2)
    VETH_A=l-${SW_A_NAME}_${SW_A_PORT}-${SW_B_NAME}_${SW_B_PORT}
    VETH_B=l-${SW_B_NAME}_${SW_B_PORT}-${SW_A_NAME}_${SW_A_PORT}
    VETH_A=${VETH_A:0:15}
    VETH_B=${VETH_B:0:15}

    ip link add dev ${VETH_A} type veth peer name ${VETH_B}
    ip link set dev ${VETH_A} up
    ip link set dev ${VETH_B} up

    ovs-vsctl add-port ${SW_A_NAME} ${VETH_A} \
      -- set interface ${VETH_A} ofport_request=${SW_A_PORT}
    ovs-vsctl add-port ${SW_B_NAME} ${VETH_B} \
      -- set interface ${VETH_B} ofport_request=${SW_B_PORT}
}

cleanup () {
    for NETNS in $(ip netns list | grep "faucet-" | awk '{print $1}'); do
        [ -n "${NETNS}" ] || continue
        NAME=${NETNS#faucet-}
        if [ -f "/run/dhclient-${NAME}.pid" ]; then
            pkill -F "/run/dhclient-${NAME}.pid"
        fi
        if [ -f "/run/iperf3-${NAME}.pid" ]; then
            pkill -F "/run/iperf3-${NAME}.pid"
        fi
        if [ -f "/run/bird-${NAME}.pid" ]; then
            pkill -F "/run/bird-${NAME}.pid"
        fi

        ip link delete veth-${NAME}
        ip netns delete ${NETNS}
    done
    for isl in $(ip -o link show | awk -F': ' '{print $2}' | grep -oE "^l-sw[0-9](_[0-9]*)?-sw[0-9](_[0-9]*)?"); do

        ip link delete dev $isl 2>/dev/null || true
    done
    for DNSMASQ in /run/dnsmasq-vlan*.pid; do
        [ -e "${DNSMASQ}" ] || continue

        pkill -F "${DNSMASQ}"
    done

    ip link delete veth-faucet 2>/dev/null || true

    # Fazer deleção de todas as switches
    ovs-vsctl --if-exists del-br sw1
    ovs-vsctl --if-exists del-br sw2
    ovs-vsctl --if-exists del-br sw3
}

create_switch () {
    SW_NAME=sw$1
    # Datapath id talvez não funcione dessa maneira
    DP_ID=$1

    ovs-vsctl add-br ${SW_NAME} \
    -- set bridge ${SW_NAME} other-config:datapath-id=${DP_ID} \
    -- set bridge ${SW_NAME} other-config:disable-in-band=true \
    -- set bridge ${SW_NAME} fail_mode=secure \
    -- set-controller ${SW_NAME} tcp:faucet:6653 tcp:gauge:6653
}

create_host () {
    HOSTNAME=$1
    IP=$2

    create_ns $HOSTNAME $IP/24
}

add_host_to_switch () {
    SW_NAME=sw$2
    IF_NAME=veth-$1
    PORT=$3

    ovs-vsctl add-port ${SW_NAME} ${IF_NAME} \
      -- set interface ${IF_NAME} ofport_request=${PORT}
}

create_redundant_stack () {
    cleanup

    echo Criando host h1 - 10.0.1.1
    create_host h1 10.0.1.1

    echo Criando host h2 - 10.0.1.2
    create_host h2 10.0.1.2

    echo Criando host h3 - 10.0.1.3
    create_host h3 10.0.1.3

    echo Criando switch sw1
    create_switch 1

    echo Criando switch sw2
    create_switch 2

    echo Criando switch sw3
    create_switch 3

    echo Adicionando h1 a sw1
    add_host_to_switch h1 1 1

    echo Adicionando h2 a sw2
    add_host_to_switch h2 2 1

    echo Adicionando h3 a sw3
    add_host_to_switch h3 3 1

    echo Criando links entre switches
    inter_switch_link sw1:2 sw2:2
    inter_switch_link sw1:3 sw3:2
    inter_switch_link sw2:3 sw3:3
}

deactivate_sw1_sw3_link () {
    ip link set down l-sw1_3-sw3_2
    ip link set down l-sw3_2-sw1_3
}

