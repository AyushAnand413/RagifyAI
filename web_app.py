from flask import Flask, request, jsonify, render_template
from agent.supervisor import AgentSupervisor

app = Flask(__name__)

# Initialize Agent once
agent = AgentSupervisor()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Empty query"}), 400

    response = agent.handle(query)
    return jsonify(response)

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8501,
        debug=False
    )
