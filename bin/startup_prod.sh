#!/bin/bash

BASE_DIR=$(dirname $0)/../
SERVICE_NAME=frontend
PSERVE=pserve
CONF_DIR=$BASE_DIR/conf
LOG_DIR=$BASE_DIR/logs

if [[ $# > 0 ]]; then
    INI=$1
else
    INI=$CONF_DIR/production.ini
fi

export INI_FILE=$(basename $INI)
export INI_PATH=$(dirname $INI)

if [[ ! -d $LOG_DIR ]]; then
    mkdir -p $LOG_DIR
fi

$PSERVE --daemon --reload --pid-file=$LOG_DIR/${SERVICE_NAME}.pid --log-file=$LOG_DIR/frontendservice.log $INI

exit 0
