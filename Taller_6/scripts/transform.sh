#!/usr/bin/env bash
set -euo pipefail

COMPOSE_CMD="docker compose"

echo "=== Transformando a Silver ==="
${COMPOSE_CMD} exec -T spark-iceberg spark-submit /home/iceberg/jobs/transform_silver.py

echo "=== Transformando a Gold ==="
${COMPOSE_CMD} exec -T spark-iceberg spark-submit /home/iceberg/jobs/transform_gold.py

echo "Transformacion completada."
