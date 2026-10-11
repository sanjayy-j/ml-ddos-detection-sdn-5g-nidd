#!/usr/bin/env bash
# Provision only the isolated Linux/WSL environment for this project.
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "$(id -u)" != 0 ]]; then
  echo 'Run this installer with sudo inside Ubuntu.' >&2
  exit 1
fi
apt-get update
apt-get install -y openvswitch-switch mininet iproute2 iputils-ping tcpdump tcpreplay curl python3-venv
if [[ ! -x "$project_root/.tools/uv" ]]; then
  curl --fail --location https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$project_root/.tools" UV_NO_MODIFY_PATH=1 sh
fi
sdn_env="${M3_SDN_ENV:-/opt/m3-sdn}"
"$project_root/.tools/uv" python install 3.12
if [[ ! -x "$sdn_env/bin/python" ]]; then
  "$project_root/.tools/uv" venv --python 3.12 "$sdn_env"
fi
"$project_root/.tools/uv" pip install --python "$sdn_env/bin/python" \
  'os-ken==3.1.1' 'setuptools<81' 'mininet==2.3.0.dev6'
"$project_root/.tools/uv" pip install --python "$sdn_env/bin/python" -e "$project_root"
service openvswitch-switch start
"$sdn_env/bin/python" "$project_root/sdn/preflight.py"
