#!/bin/sh
if [ ! -z "$PORT" ]; then
    sed -i "s/8080/$PORT/g" /etc/xray/config.json
fi
echo "Starting Xray on Port: ${PORT:-8080}"
/usr/bin/xray run -c /etc/xray/config.json