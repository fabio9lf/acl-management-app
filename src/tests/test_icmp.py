from ssh_connection import *

def test_icmp(rule, type):
    client = setup_connection(rule["src_node"]["mgmt_ip"], "root", "root")
    command = "sh -c 'sudo ping -c3 " + rule["dest_node"]["ip"] if rule["dest_node"] is not None else "0.0.0.0"  + "'"
    stdin, stdout, stderr = execute_command(client, command=command)

    close_connection(client=client)

    if rule["target"] == "DROP":
        if type["nome"] == "insert":
            assert "0 received" in stdout or "failed" in stdout or "Connection refused" not in stdout
        else:
            assert "0 received" not in stdout and "failed" not in stdout

    elif rule["target"] == "ACCEPT":
        if type["nome"] != "insert":
            assert "0 received" in stdout or "failed" in stdout or "Connection refused" not in stdout
        else:
            assert "0 received" not in stdout and "failed" not in stdout


