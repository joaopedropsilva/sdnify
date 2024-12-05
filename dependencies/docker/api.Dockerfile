FROM ubuntu:22.04

USER root
WORKDIR /root/app

COPY . .
COPY ./dependencies/docker/api.ENTRYPOINT.sh /root/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    python3.10-venv \
    && rm -rf /var/lib/apt/lists/* \
    && chmod +x /root/api.ENTRYPOINT.sh

ENTRYPOINT [ "/root/api.ENTRYPOINT.sh" ]

