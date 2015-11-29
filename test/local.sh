#!/bin/bash

ROOT_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )"/.. && pwd )

export SECRET_DIR=${ROOT_DIR}
export KAFKA_BROKER_SERVICE_HOST=localhost
export KAFKA_BROKER_SERVICE_PORT=9092

python3 ${ROOT_DIR}/app.py
