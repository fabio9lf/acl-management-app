from classi import Network
import json

def retrieve_network():
    with open("network.json", "r") as file:
        data = json.load(file)
    return Network.from_json(data)