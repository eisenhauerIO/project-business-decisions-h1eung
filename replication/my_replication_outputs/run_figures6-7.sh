#!/usr/bin/env bash
# Runs figures6-7 and copies outputs to my_replication_outputs/figures6-7/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/../Figures6-7"
OUT_DIR="$SCRIPT_DIR/figures6-7"

echo "=== Running figures6-7 ==="
cd "$SRC_DIR"
bash figures6-7.sh

echo "=== Copying outputs to my_replication_outputs/figures6-7/ ==="
cp Figure6-\(a\).eps Figure6-\(b\).eps Figure6-\(c\).eps Figure6-\(d\).eps \
   Figure6-\(d\).pdf Figure6-\(e\).eps Figure6-\(f\).eps Figure7.eps "$OUT_DIR/"

echo "=== Done. Outputs saved to: $OUT_DIR ==="
ls "$OUT_DIR"
