#!/usr/bin/env bash
set -e

# Get configuration
LOG_LEVEL=$(jq --raw-output '.log_level // "info"' /data/options.json)
PORT=$(jq --raw-output '.port // 8080' /data/options.json)

# Export environment variables
export LOG_LEVEL
export PORT
export HA_CONFIG_PATH=/config
export HA_DATA_PATH=/data

# Start the application
python /app/main.py