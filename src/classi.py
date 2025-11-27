import json
import paramiko
from dataclasses import dataclass
from typing import List

@dataclass
class Node:
    nome: str
    ip: str

    def to_dict(self):
        return {
            "nome": self.nome,
            "ip": self.ip
        }

#class Subnet:
#    def __init__(self, nome, ip):
#        self.nome = nome
#        self.ip = ip
@dataclass
class Policy:
    src_node: Node
    dest_node: Node
    protocollo: str
    target: str

    def to_dict(self):
        return {
            "source": self.src_node.to_dict(),
            "dest": self.dest_node.to_dict(),
            "protocollo": self.protocollo,
            "target": self.target
        }

    def save(self):
        with open("network.json", "r") as file:
            data = json.load(file)
        data["policy"].append(self.to_dict())
        with open("network.json", "w") as file:
            json.dump(data, file, indent=4)
    def apply(self):
        hostname = "localhost"
        port = 2223
        username = "admin"
        password = "cisco"

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostname, port=port, username=username, password=password)

        command = f"bash -c 'sudo iptables -A FORWARD -s {self.src_node.ip} -d {self.dest_node.ip} -p {self.protocollo} -j {self.target}'"
        stdin, stdout, stderr = client.exec_command(command=command)
        #stdin, stdout, stderr = client.exec_command(f"echo {password} | sudo -S {command}")
        print(stderr.read().decode())

        client.close()


        
@dataclass
class Network:
    subnets:List[Node]
    nodes:List[Node]
    policies:List[Policy]

    @staticmethod
    def from_json(data):
        return Network(
            subnets=[Node(**s) for s in data["sottoreti"]],
            nodes=[Node(**n) for n in data["nodi"]],
            policies=[Policy(**p) for p in data["policy"]]
        )
    
    def find_node_by_name(self, name):
        for subnet in self.subnets:
            if name == subnet.nome:
                return subnet
        for host in self.nodes:
            if name == host.nome:
                return host
        return None
        
    def to_dict(self):
        return {
            "sottoreti": [s.to_dict() for s in self.subnets],
            "nodi": [n.to_dict() for n in self.nodes],
            "policy": [p.to_dict() for p in self.policies]
        }    
    