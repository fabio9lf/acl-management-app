#from classi import Network
import json
from queue import Queue
import threading

def retrieve_network_as_json(path = "network.json"):
    with open(path, "r") as file:
        data = json.load(file)
    return data

def update_network(data, path = "network.json"):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)

def retrieve_from_test_result(path = "test_result.json"):
    with open(path, "r") as file:
        data = json.load(file)
    return data

def clear_test_result(path = "test_result.json"):
    with open(path, "w") as file:
        file.write("[]")


def test_result_writer(queue : Queue, STOP : object, path = "test_result.json"):
    data = []
    while True:
        item = queue.get()
        if item is STOP:
            break
        data.append(item)
        queue.task_done()
    data.sort(key=lambda x: (x["src_node"]["nome"], x["dest_node"]["nome"],x["protocollo"]))
    with open(path, "w") as file:
        json.dump(data, file, indent=4)
