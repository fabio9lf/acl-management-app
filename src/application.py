from flask import render_template, Flask, request
from lib.network import Network
from lib.policy import Policy
from lib.retrieve_network import retrieve_network_as_json

app = Flask(__name__)

@app.route("/")
def start():
    network = Network.from_json(retrieve_network_as_json())
    return render_template("index.html", network=network.__dict__)

@app.route("/aggiungi", methods=["POST"])
def aggiungi():
    data = request.get_json()
    network = Network.from_json(retrieve_network_as_json())

    network.insert_policy(data)

    return retrieve_network_as_json()

@app.route("/rimuovi", methods=["GET"])
def rimuovi():
    line_number = request.args.get("line_number")
    router_name = request.args.get("router_name")
    network = Network.from_json(retrieve_network_as_json())

    network.remove_policy(line_number, router_name)
    return retrieve_network_as_json()

@app.route("/replace", methods=["GET", "POST"])
def replace():
    line_number = request.args.get("line_number")
    router_name = request.args.get("router_name")

    data = request.get_json()

    network = Network.from_json(retrieve_network_as_json())
    network.replace_policy(line_number, router_name, data)
    
    return retrieve_network_as_json()

@app.route("/reload", methods=["GET", "POST"])
def reload():
    return retrieve_network_as_json()


if __name__ == "__main__":
    from lib.browser import open_browser
    open_browser()
    app.run(host="0.0.0.0", port=5000)