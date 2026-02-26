#!/usr/bin/env bash
set -euo pipefail

rm -f partial_replication_results.txt

conda init
eval "$(conda shell.bash hook)"

conda activate my-virtenv-py38

while IFS=' ' read -r arg1 arg2 arg3 || [ -n "$arg1" ]; do
   # skip if arg1 is empty (blank line)
  [ -z "$arg1" ] && continue
  python3 simulation_test_null.py --input-argument-1 "$arg1" --input-argument-2 "$arg2" --input-argument-3 "$arg3"
done < input_arguments_partial.txt

python3 Table3.py

# Don't fail if no files match
rm -f tiebreaking*.txt

conda deactivate