#!/bin/bash
# Active health check sidecar for open-source Nginx.
# Probes each backend's /health endpoint and rewrites upstream.conf,
# then reloads nginx only when the pool actually changed.

UPSTREAM_FILE="/etc/nginx/conf.d/upstream.conf"
TEMP_FILE="/tmp/upstream.conf.tmp"
NODES=("10.10.130.241" "10.10.130.242")
HEALTH_PATH="/health"
INTERVAL=5

# Balancing method written into the upstream block, e.g. "least_conn;"
# Empty = round robin. Change here, restart the service — not in the .conf,
# because this script owns that file.
METHOD=""

generate_config() {
    echo "upstream backend_servers {"              >  "$TEMP_FILE"
    echo "    zone backend 64k;"                   >> "$TEMP_FILE"
    [ -n "$METHOD" ] && echo "    $METHOD"         >> "$TEMP_FILE"

    for node in "${NODES[@]}"; do
        if curl -sf --max-time 2 "http://$node$HEALTH_PATH" > /dev/null; then
            echo "    server $node:80 max_fails=3 fail_timeout=30s;" >> "$TEMP_FILE"
        else
            echo "    server $node:80 down;"       >> "$TEMP_FILE"
            logger -t nginx-healthcheck "node $node unreachable, marked DOWN"
        fi
    done

    echo "    keepalive 32;"                       >> "$TEMP_FILE"
    echo "}"                                       >> "$TEMP_FILE"

    # Reload only on change — a reload every 5s would churn workers for nothing
    if ! diff -q "$TEMP_FILE" "$UPSTREAM_FILE" > /dev/null 2>&1; then
        cp "$TEMP_FILE" "$UPSTREAM_FILE"
        if nginx -t 2>/dev/null; then
            nginx -s reload
            logger -t nginx-healthcheck "pool changed, nginx reloaded"
        else
            logger -t nginx-healthcheck "generated config failed nginx -t, NOT reloading"
        fi
    fi
    rm -f "$TEMP_FILE"
}

while true; do
    generate_config
    sleep "$INTERVAL"
done
