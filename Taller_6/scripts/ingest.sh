#!/usr/bin/env bash
set -euo pipefail

COMPOSE_CMD="docker compose"

echo "=== Ingestando datos a Bronze ==="
${COMPOSE_CMD} exec -T spark-iceberg spark-submit /home/iceberg/jobs/ingest_bronze.py
echo "Ingesion completada."
