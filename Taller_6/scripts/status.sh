#!/usr/bin/env bash
set -euo pipefail

COMPOSE_CMD="docker compose"

echo "=== Estado del cluster ==="
${COMPOSE_CMD} ps
echo ""
echo "=== Interfaces disponibles ==="
echo "  Jupyter + Spark : http://localhost:8888"
echo "  Spark UI        : http://localhost:8080"
echo "  MinIO Console   : http://localhost:9001 (admin/password123)"
echo "  Iceberg REST    : http://localhost:8181"
echo "  Trino UI        : http://localhost:8085"
