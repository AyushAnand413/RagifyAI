import importlib
import io
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


def test_chat_without_upload(client):
    response = client.post("/chat", json={"query": "What is revenue?"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["answer"] == "Please upload a PDF first."


def test_empty_query(client):
    response = client.post("/chat", json={"query": ""})
    assert response.status_code == 400


def test_invalid_upload_extension(client):
    data = {"file": (io.BytesIO(b"hello"), "note.txt")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 400


def test_upload_missing_file(client):
    response = client.post("/upload", data={}, content_type="multipart/form-data")
    assert response.status_code == 400


def test_large_file_handling(client, app_module):
    app_module.app.config["MAX_CONTENT_LENGTH"] = 1
    data = {"file": (io.BytesIO(b"ab"), "doc.pdf")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 413

def test_successful_upload_and_chat(client):
    upload_data = {"file": (io.BytesIO(b"fake pdf"), "doc.pdf")}
    upload_response = client.post("/upload", data=upload_data, content_type="multipart/form-data")

    assert upload_response.status_code == 200
    upload_payload = upload_response.get_json()
    assert upload_payload["status"] == "success"

    chat_response = client.post("/chat", json={"query": "Hello"})
    assert chat_response.status_code == 200
    chat_payload = chat_response.get_json()
    assert chat_payload["answer"] == "handled: Hello"
