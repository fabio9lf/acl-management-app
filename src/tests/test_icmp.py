from ssh_connection import *

def test_icmp(rule, type):
    client = setup_connection(rule["src_node"]["mgmnt_ip"], "root", "root")
    command = "sh -c 'sudo ping -c3 " + rule["dest_node"]["ip"]  + "'"
    stdin, stdout, stderr = execute_command(client, command=command)

    close_connection(client=client)

#    result = subprocess.run(["docker", "exec", "-it", "clab-lab-h1", "sh", "-c", "ping", "-c3", rule["dest_node"]["ip"]], capture_output=True, text=True)
#    stdout = result.stdout
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


