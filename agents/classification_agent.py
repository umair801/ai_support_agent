import json
import logging
import time
from openai import OpenAI
from dotenv import load_dotenv
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from config import (
    TICKET_CATEGORIES,
    URGENCY_LEVELS,
    COMPLEXITY_CONFIG,
    MIN_CONFIDENCE_FOR_AUTO_RESOLVE,
    ALWAYS_ESCALATE_CATEGORIES,
    TicketInput,
    ClassifiedTicket
)

load_dotenv()
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def classify_ticket(ticket: TicketInput) -> ClassifiedTicket:
    prompt = f"""
        You are an expert customer support classifier for an enterprise SaaS company.

        Analyze the following support ticket and return a JSON object with exactly these fields:
        - category: one of {TICKET_CATEGORIES}
        - urgency: integer from 1 to 5 where {URGENCY_LEVELS}
        - complexity: either "simple" or "complex"
        - confidence_score: float between 0.0 and 1.0 representing your confidence

        Rules for complexity:
        - Mark as "complex" if urgency >= 4
        - Mark as "complex" if category is in {ALWAYS_ESCALATE_CATEGORIES}
        - Mark as "complex" if you are not confident (confidence_score < {MIN_CONFIDENCE_FOR_AUTO_RESOLVE})
        - Otherwise mark as "simple"

        Ticket Subject: {ticket.subject}
        Ticket Body: {ticket.body}
        Customer Email: {ticket.customer_email}

        Respond ONLY with valid JSON. No explanation. No markdown.
        """

    try:
        start_time = time.time()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise ticket classification engine. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )

        elapsed = round(time.time() - start_time, 2)
        raw = response.choices[0].message.content.strip()
        logger.info(f"Classification completed in {elapsed}s: {raw}")

        result = json.loads(raw)

        classified = ClassifiedTicket(
            customer_email=ticket.customer_email,
            customer_name=ticket.customer_name,
            subject=ticket.subject,
            body=ticket.body,
            category=result["category"],
            urgency=int(result["urgency"]),
            complexity=result["complexity"],
            confidence_score=float(result["confidence_score"])
        )

        return classified

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse classification JSON: {e} | Raw: {raw}")
        raise
    except Exception as e:
        logger.error(f"Classification agent error: {e}")
        raise


if __name__ == "__main__":
    test_ticket = TicketInput(
        customer_email="john.smith@company.com",
        customer_name="John Smith",
        subject="Cannot login to my account after password reset",
        body="I reset my password yesterday but I still cannot log in. I have tried 3 times and keep getting an error. I need access urgently as I have a client presentation tomorrow."
    )

    result = classify_ticket(test_ticket)
    print("\n--- Classification Result ---")
    print(f"Category:         {result.category}")
    print(f"Urgency:          {result.urgency}/5")
    print(f"Complexity:       {result.complexity}")
    print(f"Confidence Score: {result.confidence_score}")