run () {
    cleanup

    echo CREATING HOST H1 - 10.0.1.1
    create_host h1 10.0.1.1
    echo CREATING HOST H2 - 10.0.1.2
    create_host h2 10.0.1.2
    echo CREATING SWITCH SW1
    create_switch 1
    echo ADDING H1 TO SW1
    add_host_to_switch h1 1 1
    echo ADDING H2 TO SW1
    add_host_to_switch h2 1 2

    echo H1 PINGING H2
    exec_on h1 ping -w 15 10.0.1.2
}

