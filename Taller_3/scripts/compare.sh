#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

require_docker
compose up -d
wait_for_hdfs
wait_for_yarn
wait_for_spark

# Preparar datos
echo "Cargando dataset en HDFS..."
exec_namenode "hdfs dfs -mkdir -p /user/root ${HDFS_INPUT_DIR}"
exec_namenode "hdfs dfs -put -f /workspace/data/wordcount/*.txt ${HDFS_INPUT_DIR}/"
exec_namenode "hdfs dfs -rm -r -f ${HDFS_OUTPUT_DIR_MR} >/dev/null 2>&1 || true"
exec_namenode "hdfs dfs -rm -r -f ${HDFS_OUTPUT_DIR_SPARK} >/dev/null 2>&1 || true"

EXAMPLES_JAR="$(find_examples_jar)"

# --- MapReduce ---
echo
echo "=== [1/2] Ejecutando MapReduce ==="
START_MR=$(date +%s)
exec_namenode "hadoop jar ${EXAMPLES_JAR} wordcount ${HDFS_INPUT_DIR} ${HDFS_OUTPUT_DIR_MR}"
MR_TIME=$(($(date +%s) - START_MR))

# --- Spark ---
echo
echo "=== [2/2] Ejecutando Spark ==="
START_SPARK=$(date +%s)
exec_spark_master "spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:9000 \
  --conf spark.hadoop.dfs.client.use.datanode.hostname=true \
  /jobs/wordcount.py"
SPARK_TIME=$(($(date +%s) - START_SPARK))

# --- Resultado ---
echo
echo "=========================================="
echo "  COMPARACION DE TIEMPOS - WORDCOUNT"
echo "=========================================="
printf "  MapReduce : %3ds\n" "${MR_TIME}"
printf "  Spark     : %3ds\n" "${SPARK_TIME}"
echo "=========================================="
if [[ "${SPARK_TIME}" -gt 0 && "${MR_TIME}" -gt 0 ]]; then
  RATIO=$((MR_TIME / SPARK_TIME))
  echo "  Spark fue ~${RATIO}x mas rapido en este dataset."
fi
echo
