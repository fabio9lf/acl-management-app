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

    for protocollo in protocolli:
        policy = Policy(source, dest, protocollo, target, "0")
        policy.apply()
    return jsonify({"status":"ok", "Ricevuto": data})

@app.route("/rimuovi", methods=["GET"])
def rimuovi():
    line_number = request.args.get("line_number")
    network = Network.from_json(retrieve_network_as_json())
    network.remove_policy(line_number)
    return jsonify({"status":"ok", "Ricevuto": line_number})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)