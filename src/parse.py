import sys
import json
import yaml
from lib.network import Network, Node, Policy, Router
from ipaddress import ip_interface
from tests.ssh_connection import *
import re

def create_json(path):
    network = {
        "nodi": [],
        "sottoreti": [],
        "router": []
    }
    with open(path, "r", encoding="utf-8") as file:
        dati = yaml.safe_load(file)
    nodi = dati["topology"]["nodes"]
    for nome, info in nodi.items():
        image = info.get("image")
        mgmt_ip = info.get("mgmt-ipv4")
        if image == "frr-ssh":
            network["router"].append({
                "nome": nome,
                "mgmt_ip": mgmt_ip
            })
        else:
            network["nodi"].append({
                "nome": nome, 
                "mgmt_ip": mgmt_ip
            })
            network["sottoreti"].append({
                "nome": f"LAN{nome[len(nome) - 1]}",
                "mgmt_ip": mgmt_ip
            })
    links = dati.get("topology", {}).get("links", {})
    for link in links:
        ep1, ep2 = link["endpoints"]
        host1, int1 = ep1.split(":")
        host2, int2 = ep2.split(":")
        for nodo in network["nodi"]:
            if host1 == nodo["nome"]:
                for router in network["router"]:
                    if host2 == router["nome"]:
                        nodo["nexthop"] = host2
                        interface = int1
                        break
            elif host2 == nodo["nome"]:
                for router in network["router"]:
                    if host1 == router["nome"]:
                        nodo["nexthop"] = host1
                        interface = int2
                        break

    for nodo in network["nodi"]:
        client = setup_connection(nodo["mgmt_ip"], "root", "root")
        command = f"sh -c 'ip addr show {interface} | grep inet'"
        stdin, stdout, stderr = execute_command(client, command)
        
        line = stdout.read().decode()
        ip = line.split(" ")[5].split("/")[0]
        nodo["ip"] = ip

        close_connection(client)
    import ipaddress
    for i in range(len(network["nodi"])):
        ip_nodo = f"{network['nodi'][i]['ip']}/24"
        network["sottoreti"][i]["ip"] = f"{str(ipaddress.ip_interface(ip_nodo).network.network_address)}/24"
        network["sottoreti"][i]["nexthop"] = network["nodi"][i]["nexthop"]
                  
    parse_policy(network, path)
    return network

def parse_policy(network : dict, path):
    cartella = path.split("/")[0]
    for router in network["router"]:
        router["policy"] = []
        nome = router["nome"]
        with open(f"{cartella}/configs/{nome}/iptables.rules", "r") as file:
            line_number = 1
            for line in file:
                line = line.strip()
                if line.startswith("-A"):
                    pattern = r"-(s|d|p|j)\s+(\S+)"
                    matches = re.findall(pattern, line)
                    regola = {key: val for key, val in matches}
                    source_ip = str(regola.get("s")).split("/")[0]
                    dest_ip = str(regola.get("d")).split("/")[0]
                    proto = regola.get("p") if regola.get("p") is not None else ""
                    target = regola.get("j")
                    src_node = next((node for node in network["nodi"] if node.get("ip") == source_ip), None)
                    dest_node = next((node for node in network["nodi"] if node.get("ip") == dest_ip), None)
                    policy = {
                        "src_node": src_node,
                        "dest_node": dest_node,
                        "protocollo": proto,
                        "target": target, 
                        "line_number": str(line_number)
                    }
                    router["policy"].append(policy)
                    line_number += 1
                    


if __name__ == "__main__":
    path_yaml = sys.argv[1]
    data = create_json(path_yaml)

    with open("network.json", "w") as file:
        json.dump(data, file, indent=4)