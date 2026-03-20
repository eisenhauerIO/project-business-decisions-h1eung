#!/usr/bin/env bash
# Runs Table 3 partial replication and copies outputs to my_replication_outputs/table3_partial/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/../Table3/single_computer_codes"
OUT_DIR="$SCRIPT_DIR/table3_partial"

echo "=== Running Table 3 partial replication ==="
cd "$SRC_DIR"
bash table3_single_computer_partial.sh

echo "=== Copying outputs to my_replication_outputs/table3_partial/ ==="
cp partial_replication_results.txt Table3.txt "$OUT_DIR/"

echo "=== Done. Outputs saved to: $OUT_DIR ==="
ls "$OUT_DIR"
