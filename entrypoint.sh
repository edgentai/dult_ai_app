#!#!/usr/bin/env bash

set -ex

PYTHON=python3
RUN_GRIEVANCE_WORKER=run_grievance_worker

echo "Command received to execute $CMD_TO_EXECUTE"

run_grievance_worker(){
    echo "Starting vision worker"
    $PYTHON -m src.worker.start_grievance_worker
}

case "$CMD_TO_EXECUTE" in
    "$RUN_GRIEVANCE_WORKER")
        run_grievance_worker
        exit $?
    ;;
esac

echo "Nothing matched in entrypoint...."
echo "Exiting ...."
exit