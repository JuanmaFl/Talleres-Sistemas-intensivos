#!/usr/bin/env bash
set -euo pipefail

COMPOSE_CMD="docker compose"

echo "=== Consultando Gold con Trino ==="
echo "Conectando a Trino CLI..."
${COMPOSE_CMD} exec -T trino trino --catalog iceberg --schema lakehouse \
  --execute "SELECT region, ingresos_totales, num_transacciones FROM gold_metricas_region ORDER BY ingresos_totales DESC"
