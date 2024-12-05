FROM ubuntu:22.04

USER root
WORKDIR /root/app

COPY ./dependencies/docker/mininet.ENTRYPOINT.sh /root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    dnsutils \
    iproute2 \
    iptables \
    iputils-ping \
    mininet \
    net-tools \
    openvswitch-switch \
    openvswitch-testcontroller \
    tcpdump \
    vim \
    python3.10-venv \
    x11-xserver-utils \
    xterm \
    && rm -rf /var/lib/apt/lists/* \
    && chmod +x /root/mininet.ENTRYPOINT.sh

EXPOSE 6633 6653 6640

ENTRYPOINT ["/root/mininet.ENTRYPOINT.sh"]

