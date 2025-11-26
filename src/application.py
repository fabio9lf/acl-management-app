from flask import render_template, Flask
from classi import Network
import json

app = Flask(__name__)

@app.route("/")
def start():
    with open("network.json", "r") as file:
        data = json.load(file)
    network = Network.from_json(data)
    return render_template("index.html", network=network)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)