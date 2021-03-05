#!/bin/sh
rm dist/*
python setup.py sdist
twine upload dist/* -r pypi
