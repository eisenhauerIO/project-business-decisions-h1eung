#!/usr/bin/env bash
set -euo pipefail

conda init
eval "$(conda shell.bash hook)"

conda activate my-virtenv-py310

python3 empirical-application.py

conda deactivate
