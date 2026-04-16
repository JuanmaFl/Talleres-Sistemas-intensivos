#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

require_docker
compose up -d
wait_for_hdfs
wait_for_yarn

echo "Cargando dataset de entrada..."
exec_namenode "hdfs dfs -mkdir -p /user/root ${HDFS_INPUT_DIR}"
exec_namenode "hdfs dfs -rm -r -f ${HDFS_OUTPUT_DIR} >/dev/null 2>&1 || true"
exec_namenode "hdfs dfs -put -f /workspace/data/wordcount/*.txt ${HDFS_INPUT_DIR}/"

EXAMPLES_JAR="$(find_examples_jar)"
if [[ -z "${EXAMPLES_JAR}" ]]; then
  echo "No fue posible encontrar el jar de ejemplos de Hadoop." >&2
  exit 1
fi

echo "Ejecutando WordCount con ${EXAMPLES_JAR}..."
exec_namenode "hadoop jar ${EXAMPLES_JAR} wordcount ${HDFS_INPUT_DIR} ${HDFS_OUTPUT_DIR}"

echo
echo "Primeras lineas del resultado:"
exec_namenode "hdfs dfs -cat ${HDFS_OUTPUT_DIR}/part-r-00000 | head -n 30"
