import json
from dataclasses import dataclass
from typing import List
class Node:
    def __init__(self, nome, ip):
        self.nome = nome
        self.ip = ip

#class Subnet:
#    def __init__(self, nome, ip):
#        self.nome = nome
#        self.ip = ip

class Policy:
    def __init__(self, src_node, dest_node, protocol, target):
        self.src_node = src_node
        self.dest_node = dest_node
        self.protocol = protocol
        self.target = target
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
        
        