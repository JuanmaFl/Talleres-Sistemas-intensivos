#!/usr/bin/env bash
set -euo pipefail
COMPOSE_CMD="docker compose"
echo "=== Estado del cluster ==="
${COMPOSE_CMD} ps
echo
echo "=== Interfaces disponibles ==="
echo "  NameNode UI      : http://localhost:9870"
echo "  ResourceManager  : http://localhost:8088"
echo "  JobHistory       : http://localhost:19888"
echo "  Spark Master UI  : http://localhost:8080"
