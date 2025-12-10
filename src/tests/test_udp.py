from ssh_connection import *

def test_udp(rule, type):
    client_dest = setup_connection(rule["dest_node"]["mgmnt_ip"], "root", "root")
    command = f"sh -c 'rm -f /tmp/udp_received.log'"
    execute_command(client_dest, command)

    command = f"sh -c 'nc -u -l -p 5000 > /tmp/udp_received.log &'"
    execute_command(client_dest, command)

    client_src = setup_connection(rule["src_node"]["mgmnt_ip"], "root", "root")

    command = "sh -c 'echo test | nc -u -w3 " +  rule['dest_node']['ip'] + " 5000'"
    execute_command(client_src, command)

    stdin, stdout, stderr = execute_command(client_dest, "cat /tmp/udp_received.log")
    output = stdout.read().decode()


    close_connection(client_src)
    close_connection(client_dest)
    
    if rule["target"] == "ACCEPT":
        if type["nome"] == "insert":
            assert "test" in output
        else:
            assert "" in output
    else:
        if type["nome"] == "insert":
            assert "" in output
        else:
            assert "test" in output