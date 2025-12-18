#!/bin/bash

> test.log
containerlab destroy -ay
containerlab deploy -t topology.clab.yaml
python3 application.py &
APP_PID=$!
explorer.exe http://localhost:5000

echo "Premi CTRL+C per terminare l'applicazione"
wait "$APP_PID"
