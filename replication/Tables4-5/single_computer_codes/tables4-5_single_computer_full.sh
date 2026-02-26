#!/usr/bin/env bash
set -euo pipefail

conda init
eval "$(conda shell.bash hook)"

conda activate my-virtenv-py38

while IFS=' ' read -r arg1 arg2 arg3 arg4 arg5 arg6; do
  python3 simulation_test_alt.py --input-argument-1 "$arg1" --input-argument-2 "$arg2" --input-argument-3 "$arg3" --input-argument-4 "$arg4" --input-argument-5 "$arg5" --input-argument-6 "$arg6"
done < input_arguments.txt

python3 Tables4-5.py

# Don't fail if no files match
rm -f tiebreaking*.txt

conda deactivate