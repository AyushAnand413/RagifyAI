CREATE_TICKET_SCHEMA = {
    "action": "create_ticket",
    "department": "string",
    "priority": "Low | Medium | High",
    "description": "string"
}

SCHEDULE_MEETING_SCHEMA = {
    "action": "schedule_meeting",
    "participants": ["string"],
    "date": "YYYY-MM-DD",
    "time": "HH:MM"
}
