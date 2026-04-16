#!/usr/bin/env bash
set -euo pipefail

COMPOSE_CMD="docker compose"

echo "=== Estado del cluster ==="
${COMPOSE_CMD} ps
echo
echo "=== Interfaces disponibles ==="
echo "  Spark Master UI : http://localhost:8080"
echo "  Jupyter Lab     : http://localhost:8888 (token: taller4)"
