#!/bin/bash

> test.log
containerlab destroy -ay
containerlab deploy -t topology.clab.yaml
python3 application.py 
