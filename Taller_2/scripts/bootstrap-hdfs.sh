#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

require_docker
compose up -d
wait_for_hdfs

echo "Preparando estructura en HDFS..."
exec_namenode "hdfs dfs -mkdir -p /user/root ${HDFS_INPUT_DIR}"
exec_namenode "hdfs dfs -put -f /workspace/data/wordcount/*.txt ${HDFS_INPUT_DIR}/"
exec_namenode "hdfs dfs -ls ${HDFS_INPUT_DIR}"

echo "Datos cargados en HDFS."
