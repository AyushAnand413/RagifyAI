import json

import pytest

from agent.supervisor import AgentSupervisor


class _DummyRetriever:
    def retrieve(self, _query):
        return [
            {
                "score": 0.9,
                "chunk_id": "chunk_001",
                "section": "Overview",
                "pages": [1],
                "tables": [],
                "images": [],
                "chunk_text": "Company overview text",
            }
        ]


class _DummyReranker:
    def rerank(self, _query, results, top_k=7):
        return results[:top_k]


@pytest.fixture
def supervisor(monkeypatch):
    monkeypatch.setattr("agent.supervisor.Reranker", lambda: _DummyReranker())
    sup = AgentSupervisor()
    sup.retriever = _DummyRetriever()
    sup.tables_raw = []
    sup.doc_loaded = True
    return sup


def test_information_output_contract(supervisor, monkeypatch):
    monkeypatch.setattr("agent.supervisor.classify_intent", lambda _q: "INFORMATION")
    monkeypatch.setattr(
        supervisor.hf_client,
        "generate",
        lambda _prompt: "This is a grounded answer.",
    )

    output = supervisor.handle("What is in the report?")

    assert isinstance(output, dict)
    assert output.get("type") == "information"
    assert "answer" in output
    assert isinstance(output["answer"], str)
    assert output["answer"] == "This is a grounded answer."


def test_action_output_contract(supervisor, monkeypatch):
    monkeypatch.setattr("agent.supervisor.classify_intent", lambda _q: "ACTION")

    llm_json = json.dumps(
        {
            "department": "IT",
            "issue_summary": "VPN not working",
            "priority": "High",
        }
    )
    monkeypatch.setattr(supervisor.hf_client, "generate", lambda _prompt: llm_json)

    output = supervisor.handle("Create ticket for VPN issue")

    assert isinstance(output, dict)
    assert output.get("type") == "action"
    assert output.get("action") == "create_ticket"

    assert "department" in output and isinstance(output["department"], str)
    assert "description" in output and isinstance(output["description"], str)
    assert "priority" in output and isinstance(output["priority"], str)

    assert "issue_summary" not in output
    assert output["description"] == "VPN not working"
