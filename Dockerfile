FROM ubuntu:22.04

USER root
WORKDIR /root/test

COPY . .
COPY ENTRYPOINT.sh /root
COPY .bashrc /root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    dnsutils \
    iproute2 \
    iptables \
    iputils-ping \
    net-tools \
    openvswitch-switch \
    openvswitch-testcontroller \
    tcpdump \
    vim \
    python3.10-venv \
    && rm -rf /var/lib/apt/lists/* \
    && chmod +x /root/ENTRYPOINT.sh

EXPOSE 6633 6653 6640

ENTRYPOINT ["/root/ENTRYPOINT.sh"]

