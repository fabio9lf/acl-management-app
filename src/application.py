from flask import jsonify, render_template, Flask, request
from classi import Network, Policy
from retrieve_network import retrieve_network_as_json
import json

app = Flask(__name__)

@app.route("/")
def start():
    network = Network.from_json(retrieve_network_as_json())
    return render_template("index.html", network=network.__dict__)

@app.route("/aggiungi", methods=["POST"])
def aggiungi():
    data = request.get_json()
    network = Network.from_json(retrieve_network_as_json())

    source = network.find_node_by_name(data["source"])
    dest = network.find_node_by_name(data["dest"])
    protocolli = [p.strip() for p in data["protocolli"].split(", ")]
    target = data["target"]

    if dest is not None:
        router = network.find_node_by_name(dest.nexthop)
    elif source is not None:
        router = network.find_node_by_name(source.nexthop)
    else:
        router = None
    for protocollo in protocolli:
        policy = Policy(source, dest, protocollo, target, "0")
        if router is not None:
            router.insert_policy(policy)
        else:
            for r in network.routers:
                r.insert_policy(policy)
    return retrieve_network_as_json()

@app.route("/rimuovi", methods=["GET"])
def rimuovi():
    line_number = request.args.get("line_number")
    router_name = request.args.get("router_name")
    network = Network.from_json(retrieve_network_as_json())
    router = network.find_node_by_name(router_name)
    print(router_name)
    router.remove_policy(line_number)
    return retrieve_network_as_json()

@app.route("/replace", methods=["GET", "POST"])
def replace():
    line_number = request.args.get("line_number")
    router_name = request.args.get("router_name")

    data = request.get_json()

    network = Network.from_json(retrieve_network_as_json())
    source = network.find_node_by_name(data["source"])
    dest = network.find_node_by_name(data["dest"])
    protocolli = [p.strip() for p in data["protocolli"].split(", ")]
    target = data["target"]

    network = Network.from_json(retrieve_network_as_json())
    router = network.find_node_by_name(router_name)

    for protocollo in protocolli:
        policy = Policy(source, dest, protocollo, target, line_number)
        router.replace_policy(line_number, policy)
        line_number = str(int(line_number) + 1)

    return retrieve_network_as_json()

@app.route("/reload", methods=["GET", "POST"])
def reload():
    return retrieve_network_as_json()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)