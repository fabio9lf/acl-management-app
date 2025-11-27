
import paramiko
def setup_connection():
    
    hostname = "localhost"
    port = 2223
    username = "admin"
    password = "cisco"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostname, port=port, username=username, password=password)
    return client

def close_connection(client):
    client.close()
