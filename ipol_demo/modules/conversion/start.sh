#!/bin/sh

cd `dirname $0`
nohup bash -c "source ./venv/bin/activate && python main.py conversion.conf &" >/dev/null &