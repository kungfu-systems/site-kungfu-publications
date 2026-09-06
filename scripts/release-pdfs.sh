#!/bin/bash
set -euo pipefail

: "${RELEASE_TAG:?RELEASE_TAG must name the reviewed publication tag}"
gh release view "$RELEASE_TAG" >/dev/null 2>&1 ||
  gh release create "$RELEASE_TAG" --title "$RELEASE_TAG" --generate-notes
gh release upload "$RELEASE_TAG" _build/pdf/*.pdf _build/pdf/SHA256SUMS \
  .buildchain/artifacts/pdf-manifest.json .buildchain/artifacts/pdf-summary.json --clobber
