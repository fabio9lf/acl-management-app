import json
from dataclasses import dataclass
from typing import List
from ssh_connection import setup_connection, close_connection
from retrieve_network import retrieve_network_as_json, update_network

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
    line_number: str


    def to_dict(self):
        return {
            "src_node": self.src_node.to_dict() if self.src_node else None,
            "dest_node": self.dest_node.to_dict() if self.dest_node else None,
            "protocollo": self.protocollo,
            "target": self.target,
            "line_number": self.line_number 
        }

    def save(self):
        data = retrieve_network_as_json()
        data["policy"].append(self.to_dict())
        update_network(data)
    def apply(self):
        client = setup_connection()
        optional = [
            f"-s {self.src_node.ip}" if self.src_node else None,
            f"-d {self.dest_node.ip}" if self.dest_node else None,
            f"-p {self.protocollo}" if self.protocollo else None,
            f"-j {self.target}" if self.target else None
        ]
        command = f"bash -c 'sudo iptables -A FORWARD " + " ".join(filter(None, optional)) + "'"
        stdin, stdout, stderr = client.exec_command(command=command)
        print(stderr.read().decode())
        filtered = filter(None, optional)
        trimmed = [p[2:] if len(p) > 2 else p[-1:] for p in filtered]
        command = f"bash -c 'sudo iptables -L FORWARD --line-numbers -n | grep " + " | grep".join(trimmed) + "'"
        stdin, stdout, stderr = client.exec_command(command=command)

        self.line_number = stdout.read().decode()[0]
        close_connection(client)
        self.save()

    def remove(self):
        client = setup_connection()
        command = f"bash -c 'sudo iptables -D FORWARD " + self.line_number + "'"
        stdin, stdout, stderr = client.exec_command(command=command)
        print(stdout.read().decode() + "\n" + stderr.read().decode())
        close_connection(client=client)

        
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
            policies=[
                Policy(
                    src_node=Node(**p["src_node"]) if isinstance(p["src_node"], dict) else p["src_node"],
                    dest_node=Node(**p["dest_node"]) if isinstance(p["dest_node"], dict) else p["dest_node"],
                    protocollo=p["protocollo"],
                    target=p["target"],
                    line_number=p["line_number"]
                )
                for p in data["policy"]
            ]
        )
    
    def find_node_by_name(self, name):
        for subnet in self.subnets:
            if name == subnet.nome:
                return subnet
        for host in self.nodes:
            if name == host.nome:
                return host
        return None
        

    def remove_policy(self, number):
        number = int(number)

        to_remove = None
        for policy in self.policies:
            temp = int(policy.line_number)

            if number == temp:
                to_remove = policy
            elif temp > number and to_remove:
                policy.line_number = str(temp - 1)
        if to_remove:
            to_remove.remove()
            self.policies.remove(to_remove)
        self.save()

    def to_dict(self):
        return {
            "sottoreti": [s.to_dict() for s in self.subnets],
            "nodi": [n.to_dict() for n in self.nodes],
            "policy": [p.to_dict() for p in self.policies]
        }

    def save(self):
        with open("network.json", "w") as file:
            json.dump(self.to_dict(), file, indent=4)    
    