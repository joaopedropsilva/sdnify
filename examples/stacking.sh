run () {
    cleanup

    echo Creating host h1 - 10.0.1.1
    create_host h1 10.0.1.1
    echo Creating host h2 - 10.0.1.2
    create_host h2 10.0.1.2
    echo Creating host h3 - 10.0.1.3
    create_host h3 10.0.1.3
    echo Creating switch sw1
    create_switch 1
    echo Creating switch sw2
    create_switch 2
    echo Creating switch sw3
    create_switch 3
    echo Adding h1 to sw1
    add_host_to_switch h1 1 1
    echo Adding h2 to sw2
    add_host_to_switch h2 2 1
    echo Adding h3 to sw3
    add_host_to_switch h3 3 1

    echo Linking all switches
    inter_switch_link sw1:2 sw2:2
    inter_switch_link sw1:3 sw3:2
    inter_switch_link sw2:3 sw3:3

    echo h1 pinging h2
    exec_on h1 ping -w 15 10.0.1.2

    echo Deactivating sw1:sw3 link
    ip link set down l-sw1_3-sw3_2
    ip link set down l-sw3_2-sw1_3

    echo h1 pinging h2
    exec_on h1 ping -w 15 10.0.1.2

}

