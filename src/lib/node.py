from dataclasses import dataclass

@dataclass
class Node:
    nome: str
    ip: str
    nexthop: str
    mgmt_ip: str

    def to_dict(self):
        return {
            "nome": self.nome,
            "ip": self.ip,
            "nexthop": self.nexthop,
            "mgmt_ip": self.mgmt_ip
        }
    
    def __eq__(self, value):
        if isinstance(value, Node):
            return self.nome == value.nome and self.ip == value.ip and self.nexthop == value.nexthop and self.mgmt_ip == value.mgmt_ip
        return False
