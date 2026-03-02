from pydantic import BaseModel
from typing import List

# --- Ticket Categories ---
TICKET_CATEGORIES: List[str] = [
    "billing",
    "technical_support",
    "account_access",
    "product_question",
    "refund_request",
    "shipping",
    "complaint",
    "other"
]

# --- Urgency Level Definitions ---
URGENCY_LEVELS: dict = {
    1: "low — general inquiry, no time pressure",
    2: "minor — slight inconvenience, response within 24 hours",
    3: "moderate — customer frustrated, response within 4 hours",
    4: "high — service disruption, response within 1 hour",
    5: "critical — revenue loss or data issue, immediate response"
}

# --- Complexity Thresholds ---
COMPLEXITY_CONFIG: dict = {
    "simple": {
        "description": "Can be resolved with a standard AI response",
        "max_urgency": 3,
        "min_confidence": 0.75
    },
    "complex": {
        "description": "Requires human judgment or sensitive handling",
        "triggers": [
            "urgency >= 4",
            "confidence_score < 0.75",
            "category in ['complaint', 'refund_request']",
            "legal or billing dispute keywords detected"
        ]
    }
}

# --- Auto-Resolution Rules ---
AUTO_RESOLVE_CATEGORIES: List[str] = [
    "product_question",
    "shipping",
    "account_access",
    "technical_support"
]

ALWAYS_ESCALATE_CATEGORIES: List[str] = [
    "complaint",
    "refund_request"
]

# --- Confidence Threshold ---
MIN_CONFIDENCE_FOR_AUTO_RESOLVE: float = 0.75

# --- Response Time Targets (seconds) ---
RESPONSE_TIME_TARGETS: dict = {
    "auto_resolve": 30,
    "escalation_prep": 60
}

# --- Pydantic Model for a Ticket ---
class TicketInput(BaseModel):
    customer_email: str
    customer_name: str | None = None
    subject: str
    body: str

class ClassifiedTicket(TicketInput):
    category: str
    urgency: int
    complexity: str
    confidence_score: float

class ProcessedTicket(ClassifiedTicket):
    status: str
    ai_response: str | None = None
    escalation_reason: str | None = None
    response_time_seconds: float | None = None