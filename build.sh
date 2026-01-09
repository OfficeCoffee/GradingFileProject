#!/usr/bin/bash

set -e 

python -m venv .venv
source .venv/bin/activate

python3 -m pip install types-python-dateutil > /dev/null
