#!/usr/bin/env bash

set -euo pipefail

COMPOSE_CMD="docker compose"
HDFS_INPUT_DIR="/user/root/wordcount/input"
HDFS_OUTPUT_DIR="/user/root/wordcount/output"

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
}

find_examples_jar() {
  exec_namenode "find /opt -name 'hadoop-mapreduce-examples-*.jar' | head -n 1"
}
