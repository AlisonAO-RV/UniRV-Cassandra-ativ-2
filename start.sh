#!/bin/sh

redis-server --daemonize yes
pip freeze > requirements.txt

python ./src/main.py
