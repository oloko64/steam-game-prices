#!/usr/bin/env bash

if [[ -d "venv" ]]; then
    source venv/bin/activate
else
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

python src/steam-prices.py
