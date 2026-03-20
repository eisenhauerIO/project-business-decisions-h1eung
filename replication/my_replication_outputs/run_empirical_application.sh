#!/usr/bin/env bash
# Runs the empirical application and copies outputs to my_replication_outputs/empirical_application/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/../Empirical-Application"
OUT_DIR="$SCRIPT_DIR/empirical_application"

echo "=== Running empirical application ==="
cd "$SRC_DIR"
bash empirical-application.sh

echo "=== Copying outputs to my_replication_outputs/empirical_application/ ==="
cp Table1.txt Table2.txt Table12.txt Table13.txt "$OUT_DIR/"
cp p-values-empirical-applicaiton.txt "$OUT_DIR/"
cp Figure8.eps Figure9.eps Figure10.eps Figure11.eps Figure12.eps "$OUT_DIR/"

echo "=== Done. Outputs saved to: $OUT_DIR ==="
ls "$OUT_DIR"
