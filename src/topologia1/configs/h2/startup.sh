#!/bin/sh
ip addr add 192.168.20.2/24 dev eth1
ip link set eth1 up
ip route del default
ip route add default via 192.168.20.1