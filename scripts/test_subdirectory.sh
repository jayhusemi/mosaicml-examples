#!/bin/env bash

# Script to cd into a subdirectory, install its deps, and run its tests
#
# The tricky part here is that some modules, like flash-attn, are really
# finicky to get installed and depend on details of your environment (e.g.,
# the installed CUDA version). For these deps, we just use whatever's
# in the surrounding environment. We do this by:
#   1) Allowing the venv to use the environment's installed packages
#       via the --system-site-packages flag.
#   2) Having the pip install overwrite everything in the requirements
#       *except* a few whitelisted dependencies.

ENV_NAME="env-${1%/}"   # strip trailing slash if present

echo "Creating venv..."
python -m venv "$ENV_NAME" --system-site-packages
source "$ENV_NAME/bin/activate"

echo "Installing requirements..."
pip install --upgrade 'pip<23'
pip install 'pre-commit>=2.18.1,<3'
pip install 'pyright==1.1.296'
pip install 'pytest>=7.2.1,<8'
target=$(echo $1 | tr '_' '-' | tr '/' '-')

original_dir=$(pwd)
cd examples/$1
if [ -f requirements-cpu.txt ]; then
    pip install -r requirements-cpu.txt
elif [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "No requirements-cpu.txt or requirements.txt found in directory examples/$1"
fi
cd $original_dir

DIRECTORY="examples/$1"
cp pyproject.toml "$DIRECTORY"
cd "$DIRECTORY"

# run tests using project pytest config
python -m pytest tests
STATUS=$?

rm pyproject.toml

echo "Cleaning up venv..."
deactivate

cd -
rm -rf "$ENV_NAME"

exit $STATUS
