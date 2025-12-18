#!/bin/bash

containerlab destroy -ay
containerlab deploy -t topology.clab.yaml
python3 application.py &
explorer.exe http://localhost:5000
