from dataclasses import dataclass
from lib.policy import Policy
from tests.ssh_connection import *
import threading
from lib.thread_sync import first, second

@dataclass
class Router:
    nome: str
    mgmt_ip: str
    policies: list[Policy]
    client: any

    def connect(self):
        self.client = setup_connection(self.mgmt_ip) 
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

        index = len(self.policies)

        if new_policy.src_node is not None:
            ip_new_source = ip_network(new_policy.src_node.ip, strict=False)
        else:
            ip_new_source = ip_network("0.0.0.0/0", strict=False)
        if new_policy.dest_node is not None:
            ip_new_dest = ip_network(new_policy.dest_node.ip, strict=False)
        else:
            ip_new_dest = ip_network("0.0.0.0/0", strict=False)            

        for p in same_source:
            if p.protocollo == new_policy.protocollo:
                ip_dest = ip_network(p.dest_node.ip)
                if ip_new_dest.subnet_of(ip_dest):
                    index = int(p.line_number) - 1
                    break
        
        for p in same_dest:
            if p.protocollo == new_policy.protocollo:
                ip_source = ip_network(p.src_node.ip)
                if int(p.line_number)  > index + 1:
                    break
                elif ip_new_source.subnet_of(ip_source):
                    index = int(p.line_number) - 1
        
        
        
        self.policies.insert(index, new_policy)
        for i, p in enumerate(self.policies, start=1):
            p.line_number = str(i)

        self.connect()
        command = new_policy.command("I")
        stdin, stdout, stderr = self.execute(command)
        threading.Thread(target=new_policy.test, args=("insert",)).start()
        print(stderr.read().decode())
        self.close()

        self.save()

    def save(self):
        self.connect()
        stdin, stdout, stderr = self.execute(command="bash -c 'sudo iptables-save > /etc/iptables/rules.v4'")
        print(stderr.read().decode())
        self.close()

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
            threading.Thread(target=to_remove.test, args=("remove",)).start()
        self.save()

    def replace_policy(self, number, new_policy: Policy):
        if not new_policy:
            self.remove_policy(number)
            return
        
        new_policy.line_number = number
        int_number = int(number)

        for i, policy in enumerate(self.policies):
            temp = int(policy.line_number)
            if int_number == temp:
                removed = self.policies[i]
                self.policies[i] = new_policy
                

        self.connect()
        command = new_policy.command("R")
        self.execute(command=command)
        self.close()

        first_done = threading.Event()

        threading.Thread(target=first, args=(first_done, removed.test, "remove",)).start()
        threading.Thread(target=second, args=(first_done, new_policy.test, "insert",)).start()
        #removed.test("remove")
        #new_policy.test("insert")

        self.save()
        
    def to_dict(self):
        return {
            "nome": self.nome,
            "mgmt_ip": self.mgmt_ip,
            "policy": [p.to_dict() for p in self.policies]
        }
