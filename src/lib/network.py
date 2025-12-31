from lib.retrieve_network import update_network
from dataclasses import dataclass
from typing import List
from lib.node import Node
from lib.router import Router
from lib.policy import Policy

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
                    mgmt_ip=r["mgmt_ip"],
                    policies=[
                        Policy(
                            src_node=Node(**p["src_node"]) if isinstance(p["src_node"], dict) else p["src_node"],
                            dest_node=Node(**p["dest_node"]) if isinstance(p["dest_node"], dict) else p["dest_node"],
                            protocollo=p["protocollo"],
                            target=p["target"],
                            line_number=p["line_number"]
                        )
                        for p in r["policy"]
                    ],
                    client=None    
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
        for i, r in enumerate(self.routers):
            if r.nome == router.nome:
                self.routers[i] = router
                break

        self.save()
        return

    def to_dict(self):
        return {
            "sottoreti": [s.to_dict() for s in self.subnets],
            "nodi": [n.to_dict() for n in self.nodes],
            "router": [r.to_dict() for r in self.routers]
        }

    def save(self):
        update_network(self.to_dict())

    def test_policy(self, policy: Policy, type: str):
        from ipaddress import ip_network

        if policy.src_node is None:
            if policy.dest_node is None:
                policy.test(type, self.nodes[0], self.nodes[1])
            else:
                ip_dest = ip_network(policy.dest_node.ip)
                for n in self.nodes:
                    ip_n = ip_network(n.ip)
                    if not ip_n.subnet_of(ip_dest):
                        policy.test(type, n)
                        return
        else:
            if policy.dest_node is None:
                ip_src = ip_network(policy.src_node.ip)
                for n in self.nodes:
                    ip_n = ip_network(n.ip)
                    if not ip_n.subnet_of(ip_src):
                        policy.test(type, None, n)
                        return
            else:
                policy.test(type)

    def insert_policy(self, data):
        import threading
        source = self.find_node_by_name(data["source"])
        dest = self.find_node_by_name(data["dest"])
        protocolli = [p.strip() for p in data["protocolli"].split(", ")]
        target = data["target"]

        if dest is not None:
            router = self.find_node_by_name(dest.nexthop)
        elif source is not None:
            router = self.find_node_by_name(source.nexthop)
        else:
            router = None
        for protocollo in protocolli:
            policy = Policy(source, dest, protocollo, target, "0")
            if router is not None:
                router.insert_policy(policy)
                self.update_router_by_name(router)
            else:
                for r in self.routers:
                    r.insert_policy(policy)
                    self.update_router_by_name(r)
            threading.Thread(target=self.test_policy, args=(policy, "insert",)).start()

    def remove_policy(self, line_number, router_name):
        import threading
        router = self.find_node_by_name(router_name)
        policy = router.remove_policy(line_number)
        self.update_router_by_name(router)
        threading.Thread(target=self.test_policy, args=(policy, "remove",)).start()

    def replace_policy(self, line_number, router_name, data):
        from lib.thread_sync import first, second, threading

        source = self.find_node_by_name(data["source"])
        dest = self.find_node_by_name(data["dest"])
        protocolli = [p.strip() for p in data["protocolli"].split(", ")]
        target = data["target"]

        router = self.find_node_by_name(router_name)
        first_done = threading.Event()

        for protocollo in protocolli:
            policy = Policy(source, dest, protocollo, target, line_number)
            removed = router.replace_policy(line_number, policy)
            threading.Thread(target=first, args=(first_done, self.test_policy, (removed, "remove"),)).start()
            threading.Thread(target=second, args=(first_done, self.test_policy, (policy, "insert"),)).start()
            line_number = str(int(line_number) + 1)
        self.update_router_by_name(router)


