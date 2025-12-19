from ssh_connection import *


def test_tcp(rule, type):
    client_dest = setup_connection(rule["dest_node"]["mgmt_ip"], "root", "root")
    
    command = f"sh -c 'nc -l -p 5000 &'"
    execute_command(client_dest, command)
    
    client_src = setup_connection(rule["src_node"]["mgmt_ip"], "root", "root")
    command = "sh -c 'nc -v -w3 " +  rule['dest_node']['ip'] + " 5000'"
    stdin, stdout, stderr = execute_command(client_src, command)

    returncode = stdout.channel.recv_exit_status()

    close_connection(client=client_src)
    close_connection(client=client_dest)
    if rule["target"] == "ACCEPT":
        if type["nome"] == "insert":
            assert returncode == 0
        else:
            assert returncode != 0
    else:
        if type["nome"] == "insert":
            assert returncode != 0
        else:
            assert returncode == 0