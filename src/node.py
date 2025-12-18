from dataclasses import dataclass

@dataclass
class Node:
    nome: str
    ip: str
    nexthop: str
    mgmnt_ip: str

    def to_dict(self):
        return {
            "nome": self.nome,
            "ip": self.ip,
            "nexthop": self.nexthop,
            "mgmnt_ip": self.mgmnt_ip
        }
    
    def __eq__(self, value):
        if isinstance(value, Node):
            return self.nome == value.nome and self.ip == value.ip and self.nexthop == value.nexthop and self.mgmnt_ip == value.mgmnt_ip
        return False
