#!/bin/sh
set -eo pipefail

WORKERS=${WORKERS:-5}
WORKER_CLASS=${WORKER_CLASS:-gevent}
ACCESS_LOG=${ACCESS_LOG:--}
ERROR_LOG=${ERROR_LOG:--}
WORKER_TEMP_DIR=${WORKER_TEMP_DIR:-/dev/shm}

# echo 'Waiting CTFd to fully start'
# while ! wget -qO- $HOST_ADDR:$HOST_PORT >/dev/null 2>&1;do
#     echo -n '.'
#     sleep 1
# done
# echo 'CTFd started'

# TODO: check if db is started
echo 'starting judger'
exec gunicorn 'app:app' \
    --bind '0.0.0.0:5000' \
    --workers $WORKERS \
    --worker-tmp-dir "$WORKER_TEMP_DIR" \
    --worker-class "$WORKER_CLASS" \
    --access-logfile "$ACCESS_LOG" \
    --error-logfile "$ERROR_LOG" \
    --capture-output
