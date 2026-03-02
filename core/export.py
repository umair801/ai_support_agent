import logging
import os
import sys
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.database import get_supabase_client
from core.config import ProcessedTicket

load_dotenv()
logger = logging.getLogger(__name__)


# --- Save Single Ticket to Supabase ---
def save_ticket(ticket: ProcessedTicket) -> dict:
    client = get_supabase_client()

    record = {
        "customer_email": ticket.customer_email,
        "customer_name": ticket.customer_name,
        "subject": ticket.subject,
        "body": ticket.body,
        "category": ticket.category,
        "urgency": ticket.urgency,
        "complexity": ticket.complexity,
        "confidence_score": ticket.confidence_score,
        "status": ticket.status,
        "ai_response": ticket.ai_response,
        "escalation_reason": ticket.escalation_reason,
        "response_time_seconds": ticket.response_time_seconds,
        "resolved_at": datetime.now(tz=timezone.utc).isoformat() if ticket.status == "auto_resolved" else None
    }

    try:
        response = client.table("tickets").insert(record).execute()
        logger.info(f"Ticket saved to Supabase: {ticket.customer_email} | Status: {ticket.status}")
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"Failed to save ticket to Supabase: {e}")
        raise


# --- Fetch All Tickets from Supabase ---
def fetch_all_tickets() -> list:
    client = get_supabase_client()

    try:
        response = client.table("tickets").select("*").order("created_at", desc=True).execute()
        logger.info(f"Fetched {len(response.data)} tickets from Supabase")
        return response.data
    except Exception as e:
        logger.error(f"Failed to fetch tickets: {e}")
        raise


# --- Export Tickets to CSV ---
def export_to_csv(output_path: str = "exports/tickets_export.csv") -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    tickets = fetch_all_tickets()

    if not tickets:
        logger.warning("No tickets found to export")
        return ""

    df = pd.DataFrame(tickets)

    # Reorder columns for readability
    preferred_cols = [
        "id", "created_at", "customer_name", "customer_email",
        "subject", "category", "urgency", "complexity",
        "confidence_score", "status", "response_time_seconds",
        "escalation_reason", "resolved_at"
    ]
    existing_cols = [c for c in preferred_cols if c in df.columns]
    remaining_cols = [c for c in df.columns if c not in existing_cols]
    df = df[existing_cols + remaining_cols]

    df.to_csv(output_path, index=False)
    logger.info(f"Exported {len(df)} tickets to {output_path}")
    return output_path


if __name__ == "__main__":
    from core.orchestrator import run_pipeline

    test_tickets = [
        {
            "customer_email": "alice@company.com",
            "customer_name": "Alice Chen",
            "subject": "Where is my shipment?",
            "body": "I ordered 5 days ago and still no tracking update. Order #78432."
        },
        {
            "customer_email": "bob@enterprise.com",
            "customer_name": "Bob Martinez",
            "subject": "Demand full refund immediately",
            "body": "Your product damaged my equipment. I am demanding a full refund and compensation. This is unacceptable."
        }
    ]

    print("Processing and saving tickets...\n")

    for ticket_data in test_tickets:
        result = run_pipeline(ticket_data)
        processed_dict = result.get("processed_ticket", {})

        if processed_dict:
            processed = ProcessedTicket(**processed_dict)
            saved = save_ticket(processed)
            print(f"Saved: {processed.customer_email} | Status: {processed.status} | DB ID: {saved.get('id')}")

    print("\nExporting to CSV...")
    path = export_to_csv()
    print(f"CSV exported to: {path}")

    print("\nFetching all tickets from Supabase:")
    all_tickets = fetch_all_tickets()
    for t in all_tickets:
        print(f"  [{t.get('status')}] {t.get('customer_email')} — {t.get('subject')}")