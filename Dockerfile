FROM ubuntu:22.04

USER root
WORKDIR /root/test

COPY ENTRYPOINT.sh /root
COPY ./etc/bashrc-test-env /root/.bashrc
COPY ./etc/requirements.txt /root/requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    dnsutils \
    iproute2 \
    iperf3 \
    iptables \
    iputils-ping \
    net-tools \
    openvswitch-switch \
    openvswitch-testcontroller \
    tcpdump \
    vim \
    python3.10-venv \
    && rm -rf /var/lib/apt/lists/* \
    && chmod +x /root/ENTRYPOINT.sh \
    && python3 -m venv /root/venv \
    && bash -c 'source /root/venv/bin/activate && \
        python3 -m pip install -r /root/requirements.txt'

EXPOSE 6653 6640

ENTRYPOINT ["/root/ENTRYPOINT.sh"]

