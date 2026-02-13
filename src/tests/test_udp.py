from ssh_connection import *
import pyshark

def test_udp(rule):
    client_dest = setup_connection(rule["rule"]["dest_node"]["mgmt_ip"], "root", "root")
    
    command = f"sh -c 'nc -u -l -p 5000 > /tmp/udp_received.log &'"
    execute_command(client_dest, command)

    client_src = setup_connection(rule["rule"]["src_node"]["mgmt_ip"], "root", "root")
    for i in range(3):
        command = f"sh -c 'printf 'test{i}' | nc -u -w3 " +  rule['rule']['dest_node']['ip'] + " 5000'"
        execute_command(client_src, command)

    stdin, stdout, stderr = execute_command(client_dest, "sh -c 'cat /tmp/udp_received.log'")
    output = stdout.read().decode()


    close_connection(client_src)
    close_connection(client_dest)
    
    if rule["expected"] == "ACCEPT":
        assert "test" in output
    else:
        assert "" in output
