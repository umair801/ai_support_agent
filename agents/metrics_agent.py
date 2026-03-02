import logging
import os
import sys
from datetime import datetime, timezone
from typing import List
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from config import ProcessedTicket

load_dotenv()
logger = logging.getLogger(__name__)


def calculate_metrics(tickets: List[ProcessedTicket]) -> dict:
    if not tickets:
        logger.warning("No tickets provided for metrics calculation")
        return {}

    total = len(tickets)
    auto_resolved = [t for t in tickets if t.status == "auto_resolved"]
    escalated = [t for t in tickets if t.status == "escalated"]

    # --- Core Rates ---
    auto_resolution_rate = round(len(auto_resolved) / total * 100, 2)
    escalation_rate = round(len(escalated) / total * 100, 2)

    # --- Response Times ---
    all_times = [t.response_time_seconds for t in tickets if t.response_time_seconds is not None]
    avg_response_time = round(sum(all_times) / len(all_times), 2) if all_times else 0.0

    auto_times = [t.response_time_seconds for t in auto_resolved if t.response_time_seconds is not None]
    avg_auto_response_time = round(sum(auto_times) / len(auto_times), 2) if auto_times else 0.0

    # --- Escalation by Category ---
    escalation_by_category: dict = {}
    for ticket in escalated:
        cat = ticket.category
        escalation_by_category[cat] = escalation_by_category.get(cat, 0) + 1

    # --- Urgency Distribution ---
    urgency_distribution: dict = {}
    for ticket in tickets:
        u = str(ticket.urgency)
        urgency_distribution[u] = urgency_distribution.get(u, 0) + 1

    # --- Estimated Cost Savings ---
    # Benchmark: $1.50 per human-handled ticket vs $0.02 per AI-resolved ticket
    human_cost_per_ticket = 1.50
    ai_cost_per_ticket = 0.02
    savings = round(
        (len(auto_resolved) * (human_cost_per_ticket - ai_cost_per_ticket)), 2
    )

    metrics = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "total_tickets": total,
        "auto_resolved": len(auto_resolved),
        "escalated": len(escalated),
        "auto_resolution_rate_pct": auto_resolution_rate,
        "escalation_rate_pct": escalation_rate,
        "avg_response_time_seconds": avg_response_time,
        "avg_auto_response_time_seconds": avg_auto_response_time,
        "escalation_by_category": escalation_by_category,
        "urgency_distribution": urgency_distribution,
        "estimated_cost_savings_usd": savings
    }

    logger.info(f"Metrics calculated for {total} tickets | Auto-resolution: {auto_resolution_rate}%")
    return metrics


def print_metrics_report(metrics: dict) -> None:
    print("\n" + "=" * 50)
    print("      ENTERPRISE SUPPORT METRICS REPORT")
    print("=" * 50)
    print(f"Generated At:          {metrics.get('generated_at')}")
    print(f"Total Tickets:         {metrics.get('total_tickets')}")
    print(f"Auto-Resolved:         {metrics.get('auto_resolved')}")
    print(f"Escalated:             {metrics.get('escalated')}")
    print(f"Auto-Resolution Rate:  {metrics.get('auto_resolution_rate_pct')}%")
    print(f"Escalation Rate:       {metrics.get('escalation_rate_pct')}%")
    print(f"Avg Response Time:     {metrics.get('avg_response_time_seconds')}s")
    print(f"Avg AI Response Time:  {metrics.get('avg_auto_response_time_seconds')}s")
    print(f"Estimated Savings:     ${metrics.get('estimated_cost_savings_usd')}")
    print(f"\nEscalations by Category: {metrics.get('escalation_by_category')}")
    print(f"Urgency Distribution:    {metrics.get('urgency_distribution')}")
    print("=" * 50)


if __name__ == "__main__":
    from config import ClassifiedTicket

    sample_tickets = [
        ProcessedTicket(
            customer_email="a@test.com", customer_name="Alice",
            subject="How do I reset my password?", body="Need help resetting.",
            category="account_access", urgency=2, complexity="simple",
            confidence_score=0.95, status="auto_resolved",
            response_time_seconds=14.3
        ),
        ProcessedTicket(
            customer_email="b@test.com", customer_name="Bob",
            subject="Charged twice this month", body="Double charge on invoice.",
            category="billing", urgency=3, complexity="simple",
            confidence_score=0.81, status="auto_resolved",
            response_time_seconds=18.7
        ),
        ProcessedTicket(
            customer_email="c@test.com", customer_name="Carol",
            subject="Threatening legal action over refund", body="No refund received.",
            category="refund_request", urgency=5, complexity="complex",
            confidence_score=0.58, status="escalated",
            escalation_reason="High urgency | Category requires human handling",
            response_time_seconds=22.1
        ),
        ProcessedTicket(
            customer_email="d@test.com", customer_name="David",
            subject="App crashes on startup", body="App won't open since update.",
            category="technical_support", urgency=3, complexity="simple",
            confidence_score=0.88, status="auto_resolved",
            response_time_seconds=16.5
        ),
        ProcessedTicket(
            customer_email="e@test.com", customer_name="Eva",
            subject="Complaint about service quality", body="Very unhappy with service.",
            category="complaint", urgency=4, complexity="complex",
            confidence_score=0.62, status="escalated",
            escalation_reason="High urgency | Category requires human handling",
            response_time_seconds=19.8
        ),
    ]

    metrics = calculate_metrics(sample_tickets)
    print_metrics_report(metrics)