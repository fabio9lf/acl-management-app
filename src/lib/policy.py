import json
from dataclasses import dataclass
from lib.node import Node
from typing import List

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
    def command(self, type):
        optional = [
            f"-s {self.src_node.ip}" if self.src_node else None,
            f"-d {self.dest_node.ip}" if self.dest_node else None,
            f"-p {self.protocollo}" if self.protocollo else None,
            f"-j {self.target}" if self.target else None
        ]
        command = f"bash -c 'sudo iptables -" + type +" FORWARD " + self.line_number + " " + " ".join(filter(None, optional)) + "'"
        return command
    
    def __eq__(self, value):
        if isinstance(value, Policy):
            return self.src_node == value.src_node and self.dest_node == value.dest_node and self.line_number == value.line_number and self.protocollo == value.protocollo and self.target == value.target
        return False

    def test(self, type: str, policies: "List[Policy]", new_src: Node = None, new_dest: Node = None):
        import subprocess

        policy = self
        if self.src_node is None:
            policy.src_node = new_src
        if self.dest_node is None:
            policy.dest_node = new_dest
        
        expected = None
        blocked = False
        for p in policies:
            if self.matches(p):
                expected = p.target
                blocked = True

                if p == self:
                    blocked = False
                    if type != "insert":
                        if p.target == "DROP":
                            expected = "ACCEPT"
                        else:
                            expected = "DROP"
                break
        dict = {
            "rule": policy.to_dict(), 
            "blocked": blocked,
            "type": "policy",
            "expected": expected if not None else "DROP"
        }
        rule = json.dumps(dict)
        with open("test.log", "a") as file:
            if self.protocollo == "tcp":
                subprocess.run(["pytest", "-s", "tests/test_tcp.py", "--rule", rule], stdout=file)
            elif self.protocollo == "udp":
                subprocess.run(["pytest", "-s", "tests/test_udp.py", "--rule", rule], stdout=file)
            else:
                subprocess.run(["pytest", "-s", "tests/test_icmp.py", "--rule", rule], stdout=file)

    def matches(self, other: "Policy") -> bool:
        from ipaddress import ip_network

        if self.protocollo and other.protocollo and self.protocollo != other.protocollo:
            return False

        def ip_match(a, b):
            if a is None or b is None:
                return True  
            return ip_network(b.ip, strict=False).subnet_of(ip_network(a.ip, strict=False))

        normal_match = ip_match(self.src_node, other.src_node) and ip_match(self.dest_node, other.dest_node)

        if normal_match:
            return True

        if other.protocollo == "tcp":
            reverse_match = ip_match(self.src_node, other.dest_node) and ip_match(self.dest_node, other.src_node)
            if reverse_match:
                return True

        return False