#!/bin/bash

state=${1:-"start"}
state=$(echo "$state" | tr '[:upper:]' '[:lower:]')

# ----------------------------------------------------------
# Function to determine which docker compose command to use
# ----------------------------------------------------------
get_docker_compose_cmd() {
    if docker compose version &>/dev/null; then
        echo "docker compose"
    elif docker-compose version &>/dev/null; then
        echo "docker-compose"
    else
        echo "ERROR: Neither 'docker compose' nor 'docker-compose' is installed or available in PATH." >&2
        exit 1
    fi
}

# Detect and assign the correct compose command
DOCKER_COMPOSE_CMD=$(get_docker_compose_cmd)

case "$state" in
  start)
    $DOCKER_COMPOSE_CMD up -d
    ;;
  stop)
    $DOCKER_COMPOSE_CMD down
    ;;
  restart)
    $DOCKER_COMPOSE_CMD down
    $DOCKER_COMPOSE_CMD up -d --build
    ;;
  cleanup)
    $DOCKER_COMPOSE_CMD down --volumes
    ;;
  *)
    echo "Usage: $0 {start|stop|restart}"
    exit 1
esac