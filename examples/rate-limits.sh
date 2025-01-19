run () {
    cleanup

    echo Creating host h1 - 10.0.1.1
    create_host h1 10.0.1.1
    echo Creating host h2 - 10.0.1.2
    create_host h2 10.0.1.2
    echo Creating switch sw1
    create_switch 1
    echo Adding h1 to sw1
    add_host_to_switch h1 1 1
    echo Adding h2 to sw1
    add_host_to_switch h2 1 2

    echo Simulating http traffic
    gen_iperf_traffic h1 h2 80
    echo Simulating ftp traffic
    gen_iperf_traffic h1 h2 21
    echo Simulating voip traffic
    gen_iperf_traffic h1 h2 5001 udp
}

