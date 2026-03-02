import logging
import time
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from config import (
    URGENCY_LEVELS,
    ALWAYS_ESCALATE_CATEGORIES,
    MIN_CONFIDENCE_FOR_AUTO_RESOLVE,
    ProcessedTicket,
    ClassifiedTicket
)

load_dotenv()
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def determine_escalation_reason(ticket: ClassifiedTicket) -> str:
    reasons = []

    if ticket.urgency >= 4:
        reasons.append(f"High urgency level ({ticket.urgency}/5)")

    if ticket.category in ALWAYS_ESCALATE_CATEGORIES:
        reasons.append(f"Category '{ticket.category}' requires human handling")

    if ticket.confidence_score < MIN_CONFIDENCE_FOR_AUTO_RESOLVE:
        reasons.append(f"Low AI confidence ({ticket.confidence_score:.0%})")

    if not reasons:
        reasons.append("Marked complex by classification agent")

    return " | ".join(reasons)


def generate_context_summary(ticket: ClassifiedTicket) -> str:
    prompt = f"""
        You are a senior support team lead preparing a handoff summary for a human agent.

        Write a concise escalation brief (maximum 100 words) that includes:
        1. What the customer's issue is in one sentence
        2. Why this ticket is being escalated
        3. The recommended first action for the human agent
        4. Any urgency note if applicable

        Ticket Details:
        - Customer: {ticket.customer_name or "Unknown"} ({ticket.customer_email})
        - Category: {ticket.category}
        - Urgency: {ticket.urgency}/5 — {URGENCY_LEVELS.get(ticket.urgency, "")}
        - Confidence Score: {ticket.confidence_score:.0%}
        - Subject: {ticket.subject}
        - Message: {ticket.body}

        Write only the brief. No labels. No JSON. No markdown.
        """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a support team lead writing concise escalation briefs for human agents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Failed to generate context summary: {e}")
        return "Automated summary unavailable. Please review ticket manually."


def escalate_ticket(ticket: ClassifiedTicket) -> ProcessedTicket:
    try:
        start_time = time.time()

        escalation_reason = determine_escalation_reason(ticket)
        context_summary = generate_context_summary(ticket)

        elapsed = round(time.time() - start_time, 2)
        logger.info(f"Ticket escalated in {elapsed}s | Reason: {escalation_reason}")

        processed = ProcessedTicket(
            customer_email=ticket.customer_email,
            customer_name=ticket.customer_name,
            subject=ticket.subject,
            body=ticket.body,
            category=ticket.category,
            urgency=ticket.urgency,
            complexity=ticket.complexity,
            confidence_score=ticket.confidence_score,
            status="escalated",
            ai_response=context_summary,
            escalation_reason=escalation_reason,
            response_time_seconds=elapsed
        )

        return processed

    except Exception as e:
        logger.error(f"Escalation agent error: {e}")
        raise


if __name__ == "__main__":
    test_ticket = ClassifiedTicket(
        customer_email="sarah.johnson@enterprise.com",
        customer_name="Sarah Johnson",
        subject="Unauthorized charges on my account — threatening legal action",
        body="I have been charged three times for a subscription I cancelled two months ago. I have contacted support twice with no resolution. I am now considering legal action if this is not resolved within 24 hours. Total unauthorized charges: $847.",
        category="refund_request",
        urgency=5,
        complexity="complex",
        confidence_score=0.61
    )

    result = escalate_ticket(test_ticket)
    print("\n--- Escalation Result ---")
    print(f"Status:             {result.status}")
    print(f"Escalation Reason:  {result.escalation_reason}")
    print(f"Response Time:      {result.response_time_seconds}s")
    print(f"\nContext Summary for Human Agent:\n{result.ai_response}")