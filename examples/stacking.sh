run () {
    cleanup

    echo CREATING HOST H1 - 10.0.1.1
    create_host h1 10.0.1.1
    echo CREATING HOST H2 - 10.0.1.2
    create_host h2 10.0.1.2
    echo CREATING HOST H3 - 10.0.1.3
    create_host h3 10.0.1.3
    echo CREATING SWITCH SW1
    create_switch 1
    echo CREATING SWITCH SW2
    create_switch 2
    echo CREATING SWITCH SW3
    create_switch 3
    echo ADDING H1 TO SW1
    add_host_to_switch h1 1 1
    echo ADDING H2 TO SW2
    add_host_to_switch h2 2 1
    echo ADDING H3 TO SW3
    add_host_to_switch h3 3 1

    echo LINKING ALL SWITCHES
    inter_switch_link sw1:2 sw2:2
    inter_switch_link sw1:3 sw3:2
    inter_switch_link sw2:3 sw3:3

    echo H1 PINGING H3
    exec_on h1 ping -c 20 -i 1 10.0.1.3

    echo DEACTIVATING SW1:SW3 LINK
    ip link set down l-sw1_3-sw3_2
    ip link set down l-sw3_2-sw1_3

    echo H1 PINGING H3
    exec_on h1 ping -c 30 -i 1 10.0.1.3
}

