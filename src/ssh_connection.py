
import paramiko
def setup_connection(porta=2223):
    
    hostname = "localhost"
    username = "admin"
    password = "cisco"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostname, port=porta, username=username, password=password)
    return client

def close_connection(client):
    client.close()

def execute_command(client, command):
    return client.exec_command(command)
