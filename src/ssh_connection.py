
import paramiko
def setup_connection(porta=2223) -> paramiko.SSHClient:
    
    hostname = "localhost"
    username = "admin"
    password = "cisco"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostname, port=porta, username=username, password=password)
    return client

def close_connection(client: paramiko.SSHClient):
    client.close()

def execute_command(client: paramiko.SSHClient, command):
    return client.exec_command(command)
