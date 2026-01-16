#!/bin/sh
pip install --user -e .[dev]
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.9 3.11 3.12 3.14
