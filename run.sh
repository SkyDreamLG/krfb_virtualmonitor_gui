#!/usr/bin/env bash
# 启动 Krfb 虚拟屏管理器。
set -euo pipefail
cd "$(dirname "$0")"
exec .venv/bin/python main.py "$@"
