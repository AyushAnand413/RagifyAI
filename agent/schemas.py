# agent/schemas.py

# -----------------------------
# Planner intent labels
# -----------------------------
PLANNER_INTENTS = {
    "INFORMATION",
    "ACTION",
    "INFORMATION_AND_ACTION"
}

# -----------------------------
# Supported actions (IT-only)
# -----------------------------
SUPPORTED_ACTIONS = {
    "create_ticket",
    "schedule_meeting"
}

# -----------------------------
# Confidence gating threshold
# -----------------------------
# Actions are allowed ONLY if confidence >= threshold
PLANNER_CONFIDENCE_THRESHOLD = 0.6
