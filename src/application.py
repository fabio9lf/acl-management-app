from flask import jsonify, render_template, Flask, request
from classi import Network, Policy
from retrieve_network import retrieve_network
import json

app = Flask(__name__)

@app.route("/")
def start():
    network = retrieve_network()
    return render_template("index.html", network=network.__dict__)

@app.route("/aggiungi", methods=["POST"])
def aggiungi():
    data = request.get_json()
    network = retrieve_network()

    source = network.find_node_by_name(data["source"])
    dest = network.find_node_by_name(data["dest"])
    protocolli = data["protocolli"]
    target = data["target"]

    for protocollo in protocolli:
        policy = Policy(source, dest, protocollo, target)
        policy.save()
        #policy.apply()
    return jsonify({"status":"ok", "Ricevuto": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)