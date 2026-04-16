#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

require_docker
compose up -d
wait_for_hdfs
wait_for_spark

echo "Limpiando output anterior de Spark..."
exec_namenode "hdfs dfs -rm -r -f ${HDFS_OUTPUT_DIR_SPARK} >/dev/null 2>&1 || true"

echo "=== Ejecutando WordCount con Spark ==="
START=$(date +%s)
exec_spark_master "spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:9000 \
  --conf spark.hadoop.dfs.client.use.datanode.hostname=true \
  /jobs/wordcount.py"
SPARK_TIME=$(($(date +%s) - START))

echo
echo "Tiempo Spark: ${SPARK_TIME}s"
