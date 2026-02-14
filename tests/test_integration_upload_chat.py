import importlib
import io
import pathlib
import sys
import types

import pytest


@pytest.fixture
def app_module(monkeypatch):
    fake_supervisor_module = types.ModuleType("agent.supervisor")

    class FakeSupervisor:
        def __init__(self):
            self.doc_loaded = False

        def has_active_document(self):
            return self.doc_loaded

        def set_active_document(self, index, metadata, tables_raw):
            self.doc_loaded = True

        def handle(self, query):
            return {"type": "information", "answer": f"handled: {query}"}

    fake_supervisor_module.AgentSupervisor = FakeSupervisor
    monkeypatch.setitem(sys.modules, "agent.supervisor", fake_supervisor_module)

    fake_ingestion_module = types.ModuleType("ingestion.runtime_ingestion")

    def fake_ingest_pdf_to_runtime(_pdf_path):
        return {"index": object(), "metadata": [], "tables": []}

    fake_ingestion_module.ingest_pdf_to_runtime = fake_ingest_pdf_to_runtime
    monkeypatch.setitem(sys.modules, "ingestion.runtime_ingestion", fake_ingestion_module)

    sys.modules.pop("web_app", None)
    module = importlib.import_module("web_app")
    module.app.config["TESTING"] = True
    return module


@pytest.fixture
def client(app_module):
    return app_module.app.test_client()


def test_real_pdf_upload_then_chat(client):
    # 🔹 Correct portable fixture path
    pdf_path = pathlib.Path(__file__).parent / "fixtures" / "press.pdf"
    assert pdf_path.exists(), f"Expected fixture PDF at {pdf_path}"

    with pdf_path.open("rb") as f:
        upload_resp = client.post(
            "/upload",
            data={"file": (io.BytesIO(f.read()), "press.pdf")},
            content_type="multipart/form-data",
        )

    assert upload_resp.status_code == 200
    upload_payload = upload_resp.get_json()
    assert isinstance(upload_payload, dict)
    assert upload_payload.get("status") == "success"

    # After upload, chat should work
    chat_resp = client.post("/chat", json={"query": "Give a summary"})
    assert chat_resp.status_code == 200

    chat_payload = chat_resp.get_json()
    assert isinstance(chat_payload, dict)
    assert ("answer" in chat_payload) or ("action" in chat_payload)

    # Ensure upload guard is no longer triggered
    assert chat_payload.get("answer") != "Please upload a PDF first."
