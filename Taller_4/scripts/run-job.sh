#!/usr/bin/env bash
set -euo pipefail

COMPOSE_CMD="docker compose"

echo "Ejecutando analisis de ventas con Spark..."
${COMPOSE_CMD} exec -T spark-master spark-submit \
  --master spark://spark-master:7077 \
  /jobs/analisis_ventas.py
