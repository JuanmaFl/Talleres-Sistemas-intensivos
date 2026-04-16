#!/usr/bin/env bash

set -euo pipefail

COMPOSE_CMD="docker compose"
HDFS_INPUT_DIR="/user/root/wordcount/input"
HDFS_OUTPUT_DIR_MR="/user/root/wordcount/output-mr"
HDFS_OUTPUT_DIR_SPARK="/user/root/wordcount/output-spark"

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker no esta instalado o no esta en el PATH." >&2
    exit 1
  fi
}

compose() {
  ${COMPOSE_CMD} "$@"
}

exec_namenode() {
  compose exec -T namenode bash -c "$*"
}

exec_resourcemanager() {
  compose exec -T resourcemanager bash -c "$*"
}

exec_spark_master() {
  compose exec -T spark-master bash -c "$*"
}

wait_for_hdfs() {
  echo "Esperando a que HDFS este disponible..."
  local retries=30
  local attempt=1

  until exec_namenode "hdfs dfs -ls / >/dev/null 2>&1"; do
    if [[ "${attempt}" -ge "${retries}" ]]; then
      echo "HDFS no respondio a tiempo." >&2
      exit 1
    fi
    sleep 5
    attempt=$((attempt + 1))
  done
  echo "HDFS listo."
}

wait_for_yarn() {
  echo "Esperando a que YARN este disponible..."
  local retries=30
  local attempt=1

  until exec_resourcemanager "yarn node -list 2>/dev/null | grep -q RUNNING"; do
    if [[ "${attempt}" -ge "${retries}" ]]; then
      echo "YARN no respondio a tiempo." >&2
      exit 1
    fi
    sleep 5
    attempt=$((attempt + 1))
  done
  echo "YARN listo."
}

wait_for_spark() {
  echo "Esperando a que Spark Master este disponible..."
  local retries=20
  local attempt=1

  until exec_spark_master "curl -sf http://spark-master:8080/api/v1/applications >/dev/null 2>&1"; do
    if [[ "${attempt}" -ge "${retries}" ]]; then
      echo "Spark no respondio a tiempo." >&2
      exit 1
    fi
    sleep 5
    attempt=$((attempt + 1))
  done
  echo "Spark listo."
}

find_examples_jar() {
  exec_namenode "find /opt -name 'hadoop-mapreduce-examples-*.jar' | head -n 1"
}
