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

