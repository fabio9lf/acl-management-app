from ssh_connection import *

def test_tcp(rule):
    client_dest = setup_connection(rule["rule"]["dest_node"]["mgmt_ip"], "root", "root")
    
    command = f"sh -c 'nc -l 5000 &'"
    execute_command(client_dest, command)
    

    client_src = setup_connection(rule["rule"]["src_node"]["mgmt_ip"], "root", "root")
    command = "sh -c 'ping -c1 " + rule["rule"]["dest_node"]["ip"] + " >/dev/null'"
    
    command = "sh -c 'nc -v -w3 " +  rule["rule"]['dest_node']['ip'] + " 5000'"
    stdin, stdout, stderr = execute_command(client_src, command)

    out = stdout.read().decode() + stderr.read().decode()

    success = "open" in out or "succeeded" in out

    close_connection(client=client_src)
    close_connection(client=client_dest)

    if rule["expected"] == "ACCEPT":
        assert success
    else:
        assert not success

    if bool(rule["blocked"]):
        print("\nPacchetto intercettato da un'altra policy!")