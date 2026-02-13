#!/bin/bash

TOPO="$1"
FRR=$(docker images -q frr-ssh)
ALPINE=$(docker images -q alpine-ssh)

if [ -z "$TOPO" ]; then
    echo "Errore: devi specificare una cartella"
    exit 1
fi
if [ ! -d "$TOPO" ]; then
    echo "Errore: la cartella non esiste"
    exit 1
fi
if [ -z "$FRR" ]; then
    echo "Creazione frr-ssh..."
    ./build-frr-ssh.sh
fi
if [ -z "$ALPINE" ]; then
    echo "Creazione alpine-ssh..."
    cd alpine-ssh
    docker build -t alpine-ssh .
    cd ..
fi

source ../venv/bin/activate

> network.json
containerlab deploy -t $TOPO/topology.clab.yaml
python3 parse.py $TOPO/topology.clab.yaml

python3 application.py 
containerlab destroy -ay
