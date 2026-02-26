#!/usr/bin/env bash
set -euo pipefail

# Name of the environment
ENV_NAME="my-virtenv-py310"

# Check if the environment exists
if conda env list | grep -qE "^${ENV_NAME}\s"; then
    echo "Environment $ENV_NAME already exists. Removing conda environment: $ENV_NAME"
    conda env remove -n "$ENV_NAME" -y
else
    echo "Environment $ENV_NAME does not exist."
fi

echo "Creating conda environment: $ENV_NAME"

conda env create -f environment.yml
echo "conda environment $ENV_NAME created. Now activate it."

conda init
eval "$(conda shell.bash hook)"

conda activate my-virtenv-py310
echo "conda environment $ENV_NAME activated. Now install packages needed."

pip install -r packages.txt
echo "Packages installed."

conda deactivate
