import subprocess

def test_icmp(rule, type):
    #client = ssh_connection.setup_connection(source_port)
    #command = f"sh -c 'sudo ping -c3 {dest_addr}'"
    #stdin, stdout, stderr = ssh_connection.execute_command(client, command=command)

    result = subprocess.run(["docker", "exec", "-it", "clab-lab-h1", "sh", "-c", "ping", "-c3", rule["dest_node"]["ip"]], capture_output=True, text=True)
    stdout = result.stdout
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


