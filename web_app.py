import os
import tempfile
import traceback

from flask import Flask, request, jsonify, render_template
from werkzeug.exceptions import RequestEntityTooLarge

from agent.supervisor import AgentSupervisor
from ingestion.runtime_ingestion import ingest_pdf_to_runtime

app = Flask(__name__)

# Max 20MB
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

agent = AgentSupervisor()


# -----------------------------
# Error handlers
# -----------------------------

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({
        "success": False,
        "error": "File too large (max 20MB)."
    }), 413


@app.errorhandler(Exception)
def handle_exception(e):

    print("\n🔥 ERROR OCCURRED:")
    traceback.print_exc()

    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


# -----------------------------
# Health / Home
# -----------------------------

@app.route("/")
def home():
    return jsonify({
        "success": True,
        "data": {
            "service": "corporate-rag-backend",
            "version": "v1"
        }
    })


# -----------------------------
# CHAT (HF frontend expects /api/v1/chat)
# -----------------------------

@app.route("/api/v1/chat", methods=["POST"])
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json() or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({
            "success": False,
            "error": "Empty query"
        }), 400

    if not agent.has_active_document():

        return jsonify({
            "success": True,
            "data": {
                "type": "information",
                "answer": "Please upload a PDF first."
            }
        })

    response = agent.handle(query)

    return jsonify({
        "success": True,
        "data": response
    })


# -----------------------------
# UPLOAD (HF frontend expects /api/v1/upload)
# -----------------------------

@app.route("/api/v1/upload", methods=["POST"])
@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "No file part in request."
        }), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({
            "success": False,
            "error": "No file selected."
        }), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "success": False,
            "error": "Only PDF files allowed."
        }), 400


    temp_path = None

    try:

        # SAFE PATH FOR HF SPACES
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
            dir="/tmp"
        ) as tmp:

            temp_path = tmp.name
            file.save(temp_path)


        runtime_payload = ingest_pdf_to_runtime(temp_path)

        agent.set_active_document(
            runtime_payload["index"],
            runtime_payload["metadata"],
            runtime_payload["tables"],
        )


        return jsonify({

            "success": True,

            "data": {
                "status": "success",
                "filename": file.filename,
                "message": "PDF uploaded and indexed."
            }

        })


    except Exception as e:

        print("\n🔥 UPLOAD FAILED:")
        traceback.print_exc()

        return jsonify({

            "success": False,
            "error": str(e)

        }), 500


    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# -----------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 7860))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
