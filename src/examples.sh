# Rate limit example
create_rate_limit_example () {
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
}

# Change function to generic por on TCP or UDP 
gen_http_traffic () {
    as_ns h1 iperf3 --server --port 80 --daemon \
        --pidfile /run/iperf3-h1-80.pid
    as_ns h2 iperf3 --client 10.0.1.1 --port 80 --bandwidth 100m \
        --interval 1 --verbose
}

gen_ftp_traffic () {
    as_ns h1 iperf3 --server --port 21 --daemon \
        --pidfile /run/iperf3-h1-21.pid
    as_ns h2 iperf3 --client 10.0.1.1 --port 21 --bandwidth 100m \
        --interval 1 --verbose
}

gen_udp_traffic () {
    as_ns h1 iperf3 --server --port 5000 --daemon \
        --pidfile /run/iperf3-h1-5000.pid
    as_ns h2 iperf3 --client 10.0.1.1 --port 5000 --bandwidth 100m \
        --interval 1 --verbose --udp
}

add_policies () {
}


# Stacking example
create_stacking_example () {
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

drop_sw1_sw3_link () {
    ip link set down l-sw1_3-sw3_2
    ip link set down l-sw3_2-sw1_3
}

