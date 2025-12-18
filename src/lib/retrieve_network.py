#from classi import Network
import json

#def retrieve_network():
#    with open("network.json", "r") as file:
#        data = json.load(file)
#    return Network.from_json(data)
def retrieve_network_as_json():
    with open("network.json", "r") as file:
        data = json.load(file)
    return data
def update_network(data):
    with open("network.json", "w") as file:
        json.dump(data, file, indent=4)