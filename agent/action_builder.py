import json
from llm.ollama_client import call_ollama

EXTRACTION_PROMPT = """
Extract IT action parameters from the command.

Return STRICT JSON only.

FORMAT:
{
  "priority": "High | Normal",
  "affected_user": "... or null",
  "issue": "..."
}

COMMAND:
{query}
"""

def build_action(plan: dict, query: str) -> dict:
    raw = call_ollama(EXTRACTION_PROMPT.format(query=query))

    try:
        params = json.loads(raw)
    except Exception:
        raise ValueError("Extraction failed")

    # ---- VALIDATION / CLAMPING ----
    priority = params.get("priority", "Normal")
    if priority not in ("High", "Normal"):
        priority = "Normal"

    issue = params.get("issue") or query
    affected_user = params.get("affected_user")

    return {
        "action": plan["action_type"],
        "department": "IT",
        "priority": priority,
        "issue": issue,
        "affected_user": affected_user
    }
