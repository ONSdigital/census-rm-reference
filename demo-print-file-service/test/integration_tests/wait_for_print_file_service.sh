#!/usr/bin/env bash
echo "Waiting for [print-file-service] to be ready"

while true; do
    response=$(docker inspect dev-print-file-service -f "{{ .State.Health.Status }}")
    if [[ "$response" == "healthy" ]]; then
        echo "[print-file-service] is ready"
        break
    fi

    echo "[print-file-service] not ready ([$response] is its current state)"
    ((attempt++)) && ((attempt == 30)) && echo "[print-file-service] failed to start" && exit 1
    sleep 2s

done

echo "Containers running and alive"
