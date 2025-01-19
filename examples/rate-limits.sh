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

    echo SIMULATING HTTP TRAFFIC
    gen_iperf_traffic h1 h2 80
    echo SIMULATING FTP TRAFFIC
    gen_iperf_traffic h1 h2 21
    echo SIMULATING VOIP TRAFFIC
    gen_iperf_traffic h1 h2 5001 udp
}

