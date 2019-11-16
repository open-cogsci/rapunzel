#!/bin/bash

rm -Rf output/*
mkdir output
cp -R static/* output
python3 build-menu.py --publish
~/.local/bin/pelican -s publishconf.py
cp output/index/index.html output/index.html
python3 parse-theme.py
