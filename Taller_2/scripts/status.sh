#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

require_docker

echo "Servicios del cluster:"
compose ps
echo
echo "Interfaces:"
echo "- NameNode: http://localhost:9870"
echo "- ResourceManager: http://localhost:8088"
echo "- JobHistory: http://localhost:19888"
