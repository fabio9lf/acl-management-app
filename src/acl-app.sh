#!/bin/bash

TOPO="$1"

if [ -z "$TOPO" ]; then
    echo "Errore: devi specificare una cartella"
    exit 1
fi
if [ ! -d "$TOPO" ]; then
    echo "Errore: la cartella non esiste"
    exit 1
fi

> network.json
containerlab deploy -t $TOPO/topology.clab.yaml
python3 parse.py $TOPO/topology.clab.yaml

python3 application.py 
containerlab destroy -ay
