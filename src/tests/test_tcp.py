from ssh_connection import *


def test_tcp(rule):
    client_dest = setup_connection(rule["rule"]["dest_node"]["mgmt_ip"], "root", "root")
    
    command = f"sh -c 'nc -l -p 5000 &'"
    execute_command(client_dest, command)
    
    client_src = setup_connection(rule["rule"]["src_node"]["mgmt_ip"], "root", "root")
    command = "sh -c 'nc -v -w3 " +  rule["rule"]['dest_node']['ip'] + " 5000'"
    stdin, stdout, stderr = execute_command(client_src, command)

    returncode = stdout.channel.recv_exit_status()

    close_connection(client=client_src)
    close_connection(client=client_dest)

    if rule["expected"] == "ACCEPT":
        assert returncode == 0
    else:
        assert returncode != 0

    if bool(rule["blocked"]):
        print("\nPacchetto intercettato da un'altra policy!")