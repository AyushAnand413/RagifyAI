import json
from llm.ollama_client import call_ollama
from agent.schemas import PLANNER_INTENTS, SUPPORTED_ACTIONS

PLANNER_PROMPT = """
You are an enterprise AI planner.

Your job is to determine whether the user INTENDS TO PERFORM AN ACTION.

IMPORTANT:
- Handle spelling mistakes and typos.
- Financial or report-related queries are ALWAYS INFORMATION.
- Confidence MUST reflect certainty of ACTION intent.
- If the request could reasonably be informational, confidence MUST be < 0.6.

Return STRICT JSON only.

INTENTS:
- INFORMATION
- ACTION
- INFORMATION_AND_ACTION

SUPPORTED ACTIONS:
- create_ticket
- schedule_meeting

FORMAT:
{
  "intent": "...",
  "action_type": "... or null",
  "confidence": 0.0
}

USER QUERY:
{query}
"""

def _sanitize(plan: dict) -> dict:
    out = {
        "intent": "INFORMATION",
        "action_type": None,
        "confidence": 0.0
    }

    if plan.get("intent") in PLANNER_INTENTS:
        out["intent"] = plan["intent"]

    if plan.get("action_type") in SUPPORTED_ACTIONS:
        out["action_type"] = plan["action_type"]

    try:
        conf = float(plan.get("confidence", 0.0))
        out["confidence"] = max(0.0, min(conf, 1.0))
    except Exception:
        pass

    return out

def generate_plan(query: str) -> dict:
    raw = call_ollama(PLANNER_PROMPT.format(query=query))
    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = {}
    return _sanitize(parsed)
