
import paramiko
def setup_connection(ip="172.20.20.5", username="admin", password="cisco") -> paramiko.SSHClient:

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=username, password=password)
    return client

def close_connection(client: paramiko.SSHClient):
    client.close()

def execute_command(client: paramiko.SSHClient, command):
    return client.exec_command(command)
