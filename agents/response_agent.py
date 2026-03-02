import logging
import time
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from config import (
    URGENCY_LEVELS,
    ProcessedTicket,
    ClassifiedTicket
)

load_dotenv()
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_response(ticket: ClassifiedTicket) -> ProcessedTicket:
    customer_name = ticket.customer_name or "Valued Customer"

    prompt = f"""
        You are a professional enterprise customer support agent responding on behalf of the company.

        Write a personalized, empathetic, and helpful response to the following support ticket.

        Guidelines:
        - Address the customer by their first name: {customer_name.split()[0]}
        - Acknowledge their issue clearly in the first sentence
        - Provide a concrete resolution or next step
        - Keep the tone professional but warm
        - Keep the response between 80 and 150 words
        - End with a reassurance and your name: "Support Team"
        - Do NOT use placeholders like [link] or [phone number]

        Ticket Category: {ticket.category}
        Urgency Level: {ticket.urgency}/5 — {URGENCY_LEVELS.get(ticket.urgency, "")}
        Subject: {ticket.subject}
        Customer Message: {ticket.body}

        Write only the email response body. No subject line. No JSON.
        """

    try:
        start_time = time.time()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional customer support agent. Write clear, empathetic responses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )

        elapsed = round(time.time() - start_time, 2)
        ai_response = response.choices[0].message.content.strip()
        logger.info(f"Response generated in {elapsed}s for category: {ticket.category}")

        processed = ProcessedTicket(
            customer_email=ticket.customer_email,
            customer_name=ticket.customer_name,
            subject=ticket.subject,
            body=ticket.body,
            category=ticket.category,
            urgency=ticket.urgency,
            complexity=ticket.complexity,
            confidence_score=ticket.confidence_score,
            status="auto_resolved",
            ai_response=ai_response,
            response_time_seconds=elapsed
        )

        return processed

    except Exception as e:
        logger.error(f"Response agent error: {e}")
        raise


if __name__ == "__main__":
    test_ticket = ClassifiedTicket(
        customer_email="john.smith@company.com",
        customer_name="John Smith",
        subject="Cannot login to my account after password reset",
        body="I reset my password yesterday but I still cannot log in. I have tried 3 times and keep getting an error. I need access urgently as I have a client presentation tomorrow.",
        category="account_access",
        urgency=3,
        complexity="simple",
        confidence_score=0.92
    )

    result = generate_response(test_ticket)
    print("\n--- AI Generated Response ---")
    print(f"Status:          {result.status}")
    print(f"Response Time:   {result.response_time_seconds}s")
    print(f"\nEmail Body:\n{result.ai_response}")