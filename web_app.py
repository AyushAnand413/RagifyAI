import os
import tempfile
import uuid

from flask import Flask, g, jsonify, request
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge

from agent.supervisor import AgentSupervisor
from ingestion.runtime_ingestion import ingest_pdf_to_runtime

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

agent = AgentSupervisor()
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")


def _cors_origin(origin):
    if ALLOWED_ORIGINS == "*":
        return "*"
    allowed = [item.strip() for item in ALLOWED_ORIGINS.split(",") if item.strip()]
    if origin and origin in allowed:
        return origin
    return None


def _get_request_id():
    return getattr(g, "request_id", None)


def success_response(data=None, status_code=200):
    return (
        jsonify(
            {
                "success": True,
                "request_id": _get_request_id(),
                "data": data or {},
            }
        ),
        status_code,
    )


def error_response(code, message, status_code=400, details=None):
    payload = {
        "success": False,
        "request_id": _get_request_id(),
        "error": {"code": code, "message": message},
    }
    if details is not None:
        payload["error"]["details"] = details
    return jsonify(payload), status_code


@app.before_request
def set_request_id():
    g.request_id = str(uuid.uuid4())


@app.after_request
def add_response_headers(response):
    origin = request.headers.get("Origin")
    response_origin = _cors_origin(origin)
    if response_origin:
        response.headers["Access-Control-Allow-Origin"] = response_origin

    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Request-ID"
    response.headers["Vary"] = "Origin"

    request_id = _get_request_id()
    if request_id:
        response.headers["X-Request-ID"] = request_id

    return response


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(_e):
    return error_response(
        "FILE_TOO_LARGE",
        "File too large (max 20MB).",
        status_code=413,
    )


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return error_response(
        code=f"HTTP_{e.code}",
        message=e.description,
        status_code=e.code,
    )


@app.errorhandler(Exception)
def handle_unexpected_error(_e):
    return error_response("INTERNAL_ERROR", "Internal server error.", status_code=500)


@app.route("/")
def home():
    return success_response({"service": "corporate-rag-backend", "version": "v1"})


def _chat_handler():
    data = request.get_json() or {}
    query = data.get("query", "").strip()

    if not query:
        return error_response("EMPTY_QUERY", "Query cannot be empty.", status_code=400)

    if not agent.has_active_document():
        return error_response(
            "DOCUMENT_NOT_READY",
            "Please upload a PDF first.",
            status_code=409,
        )

    response = agent.handle(query)
    return success_response(response)


def _upload_handler():
    if "file" not in request.files:
        return error_response("MISSING_FILE", "No file part in request.", status_code=400)

    file = request.files["file"]

    if not file.filename:
        return error_response("EMPTY_FILENAME", "No file selected.", status_code=400)

    if not file.filename.lower().endswith(".pdf"):
        return error_response("INVALID_FILE_TYPE", "Only PDF files are allowed.", status_code=400)

    mimetype = (file.mimetype or "").lower().strip()
    allowed_mimetypes = {"application/pdf", "application/x-pdf", "application/octet-stream"}
    if mimetype and mimetype not in allowed_mimetypes:
        return error_response(
            "INVALID_MIME_TYPE",
            "Uploaded file must be a PDF.",
            status_code=400,
            details={"mimetype": mimetype},
        )

    signature = file.stream.read(5)
    file.stream.seek(0)
    if signature != b"%PDF-":
        return error_response(
            "INVALID_FILE_CONTENT",
            "Uploaded file is not a valid PDF.",
            status_code=400,
        )

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

        return success_response(
            {
                "status": "success",
                "message": "PDF uploaded and indexed.",
                "filename": file.filename,
            }
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.route("/api/v1/chat", methods=["POST", "OPTIONS"])
def api_v1_chat():
    if request.method == "OPTIONS":
        return "", 204
    return _chat_handler()


@app.route("/api/v1/upload", methods=["POST", "OPTIONS"])
def api_v1_upload():
    if request.method == "OPTIONS":
        return "", 204
    return _upload_handler()


# Backward-compatible aliases during migration.
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return "", 204
    return _chat_handler()


@app.route("/upload", methods=["POST", "OPTIONS"])
def upload():
    if request.method == "OPTIONS":
        return "", 204
    return _upload_handler()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    app.run(host="0.0.0.0", port=port, debug=False)
