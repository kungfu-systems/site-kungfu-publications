#!/bin/bash
set -euo pipefail

: "${RELEASE_TAG:?RELEASE_TAG must name the reviewed publication tag}"
exec python3 scripts/publish.py release "$@"
