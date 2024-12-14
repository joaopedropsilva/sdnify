#!/usr/bin/bash

PROJECT_ROOT=$(dirname "$(realpath "$0")")
FAUCET_LOG_DIR="$PROJECT_ROOT/var/log/faucet"

echo [setup] Criando diretórios de logs do faucet

mkdir -p $FAUCET_LOG_DIR

files=("faucet.log" "faucet_exception.log" "gauge.log" "gauge_exception.log")

for file in "${files[@]}"; do
    touch "$FAUCET_LOG_DIR/$file"
done

echo [setup] Criação finalizada com sucesso!

