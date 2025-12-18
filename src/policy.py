import json
from dataclasses import dataclass
from node import Node

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

    def test(self, type: str):
        import subprocess

        rule = json.dumps(self.to_dict())
        if self.protocollo == "tcp":
            result = subprocess.run(["pytest", "tests/test_tcp.py", "--rule", rule, "--type", "{\"nome\": \""  + str(type) + "\"} > log.txt"], capture_output=True, text=True)
        elif self.protocollo == "udp":
            result = subprocess.run(["pytest", "tests/test_udp.py", "--rule", rule, "--type", "{\"nome\": \""  + str(type) + "\"}"], capture_output=True, text=True)
        else:
            result = subprocess.run(["pytest", "tests/test_icmp.py", "--rule", rule, "--type", "{\"nome\": \""  + str(type) + "\"}"], capture_output=True, text=True)
        print(result.stdout)
