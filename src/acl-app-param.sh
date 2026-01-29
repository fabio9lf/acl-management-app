#!/bin/bash

TOPO="$1"
N="$2"
ACL_APP="./acl_app.sh"
AUTO_CHOICE=""

while getopts ":yn" opt;do
    case $opt in
        y) AUTO_CHOICE="y" ;;
        n) AUTO_CHOICE="n" ;;
    esac
done

if ! command -v ipcalc &> /dev/null; then
    echo "ipcalc non trovato, installazione in corso..."
    sudo apt-get update
    sudo apt-get install -y ipcalc
fi

if [ -z "$TOPO" ]; then
    echo "Errore: devi specificare una cartella"
    exit 1
fi
if [[ -d "$TOPO" && "$TOPO" != "/" && "$TOPO" != "" ]]; then
    while true; do
        read -t 10 -p "La cartella '$TOPO' esite. Eliminarla? [y/n]: " yn
        case "$yn" in 
            [Yy]*)
                rm -rf "$TOPO"
                echo "Cartella eliminata"
                break
                ;;
            [Nn]*)
                echo "Avvio applicazione con topologia già creata!"
                bash "$ACL_APP" "$TOPO"
                exit 0
                ;;
            *)
                echo "Rispondi y o n!"
                ;;
        esac
    done
fi
if [ -z "$N" ]; then
    echo "Errore: devi specificare un numero di host/router"
    exit 1
fi
mkdir "$TOPO"
cd "$TOPO"
mkdir "configs"
cd "configs"
for i in $(seq 1 $N);do
    host="h$i"
    router="r$i"
    mkdir "$host"
    mkdir "$router"
    touch "$host/startup.sh"
    touch "frr-daemons.cfg"
    cat > "frr-daemons.cfg"<<EOF
bgpd=yes
ospfd=yes
ospf6d=yes
ripd=yes
ripngd=no
isisd=yes
pimd=yes
ldpd=yes
nhrpd=yes
eigrpd=no
babeld=no
sharpd=no
pbrd=no
bfdd=yes
fabricd=no
vrrpd=no
EOF
    index=$((i * 10))
    cat > "$host/startup.sh" <<EOF
#!/bin/sh
ip addr add 192.168.$index.2/24 dev eth1
ip link set eth1 up
ip route del default
ip route add default via 192.168.$index.1
EOF

    chmod +x "$host/startup.sh"

    touch "$router/iptables.rules"
    touch "$router/frr.conf"
    chmod 777 "$router/frr.conf"
    cat > "$router/frr.conf" <<EOF
hostname $router
!
interface eth1
 ip address 192.168.$index.1/24
 no sh
exit
EOF

done
link_index=0
for i in $(seq 1 $N);do
    router_i="r$i"
    eth_count=2

    for j in $(seq $((i+1)) $N);do
        router_j="r$j"

        ip_i="10.10.$link_index.1/30"
        ip_j="10.10.$link_index.2/30"

        cat >> "$router_i/frr.conf" <<EOF
!
interface eth$eth_count
 ip address $ip_i
 no sh
exit
EOF

        eth_count=$((eth_count+1))

        eth_count_j=$(grep -c "interface eth" "$router_j/frr.conf")
        eth_count_j=$((eth_count_j+1))

        cat >> "$router_j/frr.conf" <<EOF
!
interface eth$eth_count_j
 ip address $ip_j
 no sh
exit
EOF
        link_index=$((link_index+1))
    done
done

for i in $(seq 1 $N); do
    router="r$i"
    config_file="$router/frr.conf"

    {
        echo "!"
        echo "router rip"
        echo " version 2"

        grep "ip address" "$config_file" | awk '{print $3}' | while read -r addr; do
            network=$(LC_ALL=C ipcalc -n "$addr" | grep "^Network" | awk '{print $2}')
            echo " network $network"
        done

        echo " redistribute connected"
        echo "exit"
    } >> "$config_file"
done

cd ..
containerlab gen -t template.clab.yaml --vars n="$N" > topology.clab.yaml
cat topology.yaml