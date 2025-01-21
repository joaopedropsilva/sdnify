#!/usr/bin/bash

PROJECT_ROOT=$(dirname "$(realpath "$(dirname "$0")")")

SOURCE_NAME=$1 

DIRS_TO_CHECK=("$PROJECT_ROOT" "$PROJECT_ROOT/examples")
if [ "$2" == "--base-dir" ]; then
    DIRS_TO_CHECK=("$3" "${DIRS_TO_CHECK[@]}")
fi

JSON_LOCATION=''
SH_LOCATION=''
INDEX=0
while [[ -z $JSON_LOCATION && -z $SH_LOCATION && $INDEX -lt ${#DIRS_TO_CHECK[@]} ]]; do
    JSON_LOCATION=$(find "${DIRS_TO_CHECK[$INDEX]}" -type f -name "$SOURCE_NAME.json" 2>/dev/null | head -n 1)
    SH_LOCATION=$(find "${DIRS_TO_CHECK[$INDEX]}" -type f -name "$SOURCE_NAME.sh" 2>/dev/null | head -n 1)
    ((INDEX++))
done

if [[ -z $JSON_LOCATION ]]; then
    echo "$SOURCE_NAME.json not found! exiting..."
    exit
fi
if [[ -z $SH_LOCATION ]]; then
    echo "$SOURCE_NAME.sh not found! exiting..."
    exit
fi

cd $PROJECT_ROOT
python -m src.run "$JSON_LOCATION"
cd - > /dev/null

source $PROJECT_ROOT/src/ovs.sh
source $SH_LOCATION
run

