from ssh_connection import *
def test_icmp(rule):
    client = setup_connection(rule["rule"]["src_node"]["mgmt_ip"], "root", "root")
    command = "sh -c 'sudo ping -c3 " + rule["rule"]["dest_node"]["ip"] if rule["rule"]["dest_node"] is not None else "0.0.0.0"  + "'"
    stdin, stdout, stderr = execute_command(client, command=command)

    close_connection(client=client)

    if rule["expected"] == "DROP":
        assert "0 received" in stdout or "failed" in stdout or "Connection refused" not in stdout
    else:
         assert "0 received" not in stdout and "failed" not in stdout

