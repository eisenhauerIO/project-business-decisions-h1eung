#!/usr/bin/env bash
set -euo pipefail

conda init
eval "$(conda shell.bash hook)"

conda activate my-virtenv-py38

while IFS=' ' read -r arg1 arg2; do
  python3 simulation_test_null_ER_g12.py --input-argument-1 "$arg1" --input-argument-2 "$arg2"
  python3 simulation_test_null_RG_g12.py --input-argument-1 "$arg1" --input-argument-2 "$arg2"
  python3 simulation_test_null_RG_g45.py --input-argument-1 "$arg1" --input-argument-2 "$arg2"
  python3 simulation_test_null_WS_0.2.py --input-argument-1 "$arg1" --input-argument-2 "$arg2"
  python3 simulation_test_null_WS_0.8.py --input-argument-1 "$arg1" --input-argument-2 "$arg2"
  python3 simulation_test_null_WS_0.275.py --input-argument-1 "$arg1" --input-argument-2 "$arg2"
done < input_arguments.txt

python3 Table3.py

# Don't fail if no files match
rm -f tiebreaking*.txt

conda deactivate