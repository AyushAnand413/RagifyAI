import os
import tempfile

from flask import Flask, request, jsonify, render_template
from werkzeug.exceptions import RequestEntityTooLarge

from agent.supervisor import AgentSupervisor
from ingestion.runtime_ingestion import ingest_pdf_to_runtime

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

agent = AgentSupervisor()


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({"error": "File too large (max 20MB)."}), 413


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Empty query"}), 400

    if not agent.has_active_document():
        return jsonify({
            "type": "information",
            "answer": "Please upload a PDF first."
        })

    response = agent.handle(query)
    return jsonify(response)


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request."}), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({"error": "No file selected."}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are allowed."}), 400

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            temp_path = tmp.name
            file.save(temp_path)

        runtime_payload = ingest_pdf_to_runtime(temp_path)
        agent.set_active_document(
            runtime_payload["index"],
            runtime_payload["metadata"],
            runtime_payload["tables"],
        )

        return jsonify({
            "status": "success",
            "message": "PDF uploaded and indexed.",
            "filename": file.filename
        })
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8501, debug=False)
