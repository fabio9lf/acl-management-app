from lib.file_management import update_network, test_result_writer
from dataclasses import dataclass
from typing import List
from lib.node import Node
from lib.router import Router
from lib.policy import Policy
import threading
from queue import Queue

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
        
    def first_not_in_subnet(self, subnet):
        from ipaddress import ip_network
        return next(n for n in self.nodes if not ip_network(n.ip, strict=False).subnet_of(subnet))

    def test_policy(self, policy: Policy, type: str):
        from ipaddress import ip_network
        

        src, dst = policy.src_node, policy.dest_node
        router = self.find_node_by_name(src.nexthop if src is not None else dst.nexthop if dst is not None else None)
        if router is None:
            router = self.routers[0] 
        if src is None and dst is None:
            return policy.test(type, router.policies, self.nodes[0], self.nodes[1])

        if src is None:
            n = self.first_not_in_subnet(ip_network(dst.ip))
            return policy.test(type, router.policies, n)

        if dst is None:
            n = self.first_not_in_subnet(ip_network(src.ip))
            return policy.test(type, router.policies, None, n)

        policy.test(type, router.policies)
        

    def insert_policy(self, data):
        import threading
        source = self.find_node_by_name(data["source"])
        dest = self.find_node_by_name(data["dest"])
        protocolli = [p.strip() for p in data["protocolli"].split(", ")]
        target = data["target"]

        if source is not None:
            router = self.find_node_by_name(source.nexthop)
        elif dest is not None:
            router = self.find_node_by_name(dest.nexthop)
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


    def test_connectivity(self):
        queue = Queue()
        STOP = object()
        threads = []
        for src in self.nodes:
            for dest in self.nodes:
                if src == dest:
                    continue
                for proto in ("icmp", "udp", "tcp"):
                    threads.append(threading.Thread(
                        target=self.test,
                        args=(proto,src, dest,queue,)
                    ))
        writer = threading.Thread(target=test_result_writer, args=(queue, STOP,))
        writer.start()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        queue.put(STOP) 
        writer.join()

    def test(self, protocol:str, src_node: Node, dest_node: Node, queue : Queue):
        import subprocess, json, tempfile
        policy = Policy(src_node=src_node, dest_node=dest_node, protocollo=protocol, target="ACCEPT", line_number=-1)
        
        expected = "ACCEPT"
        routers = [self.find_node_by_name(src_node.nexthop), self.find_node_by_name(dest_node.nexthop)]
        for router in routers:
            router_expected = "ACCEPT"
            for p in router.policies:
                if p.matches(policy):
                    router_expected = p.target
                    break
            if router_expected == "DROP":
                expected = "DROP"
                break

        test_dict = {
            "rule": policy.to_dict(),
            "blocked": False,
            "expected": expected,
            "type": "network"
        }

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as file:
            json.dump(test_dict, file)
            tmpfile = file.name

        test_file = f"tests/test_{protocol}.py"
        result = subprocess.run(["pytest", test_file, "--rule-file", tmpfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #print(result.stdout.decode())
        #print(result.stderr.decode())

        queue.put({
            "risultato": result.returncode == 0,
            "src_node": src_node.to_dict(),
            "dest_node": dest_node.to_dict(),
            "protocollo": protocol,
            "esito": expected
        })