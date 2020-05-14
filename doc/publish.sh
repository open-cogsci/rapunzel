#!/bin/bash

rm -Rf output/*
mkdir output
cp -R static/* output
python build-menu.py --publish
pelican -s publishconf.py
cp output/index/index.html output/index.html
python parse-theme.py
