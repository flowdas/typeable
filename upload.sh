#!/bin/sh
python3 -m venv .upload
.upload/bin/python -m pip install twine
.upload/bin/python -m twine upload -r pypi dist/*
rm -rf .upload
