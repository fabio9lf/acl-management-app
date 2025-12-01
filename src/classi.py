import json
from dataclasses import dataclass
from typing import List
from ssh_connection import setup_connection, close_connection, execute_command
from retrieve_network import retrieve_network_as_json, update_network

@dataclass
class Node:
    nome: str
    ip: str
    nexthop: str

    def to_dict(self):
        return {
            "nome": self.nome,
            "ip": self.ip,
            "nexthop": self.nexthop
        }
    
    def __eq__(self, value):
        if isinstance(value, Node):
            return self.nome == value.nome and self.ip == value.ip and self.nexthop == value.nexthop
        return False

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

    #def save(self):
        #data = retrieve_network_as_json()
        #data["policy"].append(self.to_dict())
        #update_network(data)
    #    network = Network.from_json(retrieve_network_as_json())
    #   network.policies.insert(self)
    #def apply(self):
    #    optional = [
    #        f"-s {self.src_node.ip}" if self.src_node else None,
    #       f"-d {self.dest_node.ip}" if self.dest_node else None,
    #      f"-p {self.protocollo}" if self.protocollo else None,
    #        f"-j {self.target}" if self.target else None
    #    ]
    #    command = f"bash -c 'sudo iptables -A FORWARD " + " ".join(filter(None, optional)) + "'"
    #    stdin, stdout, stderr = client.exec_command(command=command)
    #    print(stderr.read().decode())
    #    filtered = filter(None, optional)
    #    trimmed = [p[2:] if len(p) > 2 else p[-1:] for p in filtered]
    #    command = f"bash -c 'sudo iptables -L FORWARD --line-numbers -n | grep " + " | grep".join(trimmed) + "'"
    #    stdin, stdout, stderr = client.exec_command(command=command)

    #    self.line_number = stdout.read().decode()[0]
    #    close_connection(client)
    #    self.save()
    def command(self):
        optional = [
            f"-s {self.src_node.ip}" if self.src_node else None,
            f"-d {self.dest_node.ip}" if self.dest_node else None,
            f"-p {self.protocollo}" if self.protocollo else None,
            f"-j {self.target}" if self.target else None
        ]
        command = f"bash -c 'sudo iptables -I " + self.line_number + " FORWARD " + " ".join(filter(None, optional)) + "'"
        return command
    def remove(self):
        client = setup_connection()
        command = f"bash -c 'sudo iptables -D FORWARD " + self.line_number + "'"
        stdin, stdout, stderr = client.exec_command(command=command)
        print(stdout.read().decode() + "\n" + stderr.read().decode())
        close_connection(client=client)

    def __eq__(self, value):
        if isinstance(value, Policy):
            return self.src_node == value.src_node and self.dest_node == value.dest_node and self.line_number == value.line_number and self.protocollo == value.protocollo and self.target == value.target
        return False

@dataclass
class Router:
    nome: str
    porta: int
    policies: list[Policy]
    client: any

    def connect(self):
        self.client = setup_connection(self.porta) 
    def close(self):
        close_connection(client=self.client)
    def execute(self, command):
        return execute_command(self.client, command=command)
    def insert_policy(self, new_policy: Policy):
        from ipaddress import ip_network, ip_address

        if new_policy in self.policies:
            return
        
        same_source = [p for p in self.policies if p.src_node == new_policy.src_node]
        same_dest = [p for p in self.policies if p.dest_node == new_policy.dest_node]

        index = self.policies.count()

        ip_new_source = ip_network(new_policy.src_node.ip, strict=False)
        ip_new_dest = ip_network(new_policy.dest_node.ip, strict=False)

        for p in same_source:
            ip_dest = ip_network(p.dest_node.ip)
            if ip_new_dest.subnet_of(ip_dest):
                index = int(p.line_number) - 1
                break
        
        for p in same_dest:
            ip_source = ip_network(p.src_node.ip)
            if int(p.line_number)  > index + 1:
                break
            elif ip_new_source.subnet_of(ip_source):
                index = int(p.line_number) - 1
        
        self.connect()
        command = new_policy.command()
        stdin, stdout, stderr = self.execute(command)
        print(stdout.read().decode())
        self.close()
        
        self.policies.insert(index, new_policy)
        for i, p in enumerate(self.policies, start=1):
            p.line_number = str(i)
        self.save()

    def save(self):
        network = Network.from_json(retrieve_network_as_json())
        network.update_router_by_name(self.nome)

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
            self.connect()
            self.execute(command=f"bash -c 'sudo iptables -D FORWARD " + to_remove.line_number +"'")
            self.close()
            self.policies.remove(to_remove)
        self.save()

    def to_dict(self):
        return {
            "nome": self.nome,
            "porta": self.porta,
            "policy": [p.to_dict() for p in self.policies]
        }

@dataclass
class Network:
    subnets:List[Node]
    nodes:List[Node]
    #policies:List[Policy]
    routers: List[Router]


    @staticmethod
    def from_json(data):
        return Network(
            subnets=[Node(**s) for s in data["sottoreti"]],
            nodes=[Node(**n) for n in data["nodi"]],
            routers=[
                Router(
                    nome=r["nome"],
                    porta=r["porta"],
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
                for r in data["router"]
            ]
        )
    
    def find_node_by_name(self, name):
        for subnet in self.subnets:
            if name == subnet.nome:
                return subnet
        for host in self.nodes:
            if name == host.nome:
                return host
        for router in self.routers:
            if name == router.nome:
                return router
        return None
        
    def update_router_by_name(self, router: Router):
        for r in self.routers:
            if r.nome == router.nome:
                r = router
                self.save()
                return

    def to_dict(self):
        return {
            "sottoreti": [s.to_dict() for s in self.subnets],
            "nodi": [n.to_dict() for n in self.nodes],
            "rotuer": [r.to_dict() for r in self.routers]
        }

    def save(self):
        with open("network.json", "w") as file:
            json.dump(self.to_dict(), file, indent=4)    