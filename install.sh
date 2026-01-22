#!/bin/sh
pip install --user -e .[dev]
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.11 3.12 3.14 3.15 pypy-3.10
