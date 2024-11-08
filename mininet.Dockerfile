FROM ubuntu:22.04

USER root
WORKDIR /root/app

COPY . .

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    dnsutils \
    iproute2 \
    iptables \
    iputils-ping \
    mininet \
    net-tools \
    tcpdump \
    vim \
    python3.10-venv \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf ./.venv \
    && /root/app/create_env.sh

EXPOSE 6653

