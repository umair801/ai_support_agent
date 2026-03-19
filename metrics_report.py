"""
metrics_report.py
Pulls live metrics from the deployed support agent and prints a business summary.
"""

import httpx
import json
from datetime import datetime

BASE_URL = "https://support.datawebify.com"

def fetch_metrics() -> dict:
    """Fetch metrics from the live API."""
    try:
        response = httpx.get(f"{BASE_URL}/metrics", timeout=15)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"Error fetching metrics: {e}")
        return {}

def fetch_health() -> dict:
    """Fetch health status from the live API."""
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=15)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"Error fetching health: {e}")
        return {}

def print_business_report(metrics: dict, health: dict) -> None:
    """Print a formatted business metrics report."""
    print("\n" + "=" * 60)
    print("  ENTERPRISE AI SUPPORT AGENT — BUSINESS METRICS REPORT")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    print("\n  SYSTEM STATUS")
    print(f"  Deployment:     support.datawebify.com")
    print(f"  Health:         {health.get('status', 'unknown').upper()}")
    print(f"  Environment:    {health.get('environment', 'production')}")

    print("\n  TICKET PROCESSING")
    data = metrics.get("metrics", metrics)
    total = data.get("total_tickets", 0)
    resolved = data.get("auto_resolved", 0)
    escalated = data.get("escalated", 0)
    resolution_rate = data.get("auto_resolution_rate_pct", 0)
    avg_response = data.get("avg_response_time_seconds", 0)

    print(f"  Total Tickets Processed:    {total}")
    print(f"  Auto-Resolved (AI):         {resolved}")
    print(f"  Escalated to Human:         {escalated}")
    print(f"  Auto-Resolution Rate:       {resolution_rate:.1f}%  (target: 60-70%)")
    print(f"  Avg Response Time:          {avg_response:.1f}s   (target: <30s)")

    print("\n  BUSINESS IMPACT (per 10,000 tickets/month)")
    human_cost_per_ticket = 1.20
    ai_cost_per_ticket = 0.08
    auto_resolved_pct = resolution_rate / 100

    ai_handled = int(10000 * auto_resolved_pct)
    human_handled = 10000 - ai_handled

    old_cost = 10000 * human_cost_per_ticket
    new_cost = (ai_handled * ai_cost_per_ticket) + (human_handled * human_cost_per_ticket)
    savings = old_cost - new_cost
    hours_saved = ai_handled * 0.05

    print(f"  Before (manual team):       ${old_cost:,.0f}/month")
    print(f"  After  (AI + escalation):   ${new_cost:,.0f}/month")
    print(f"  Monthly Savings:            ${savings:,.0f}")
    print(f"  Agent Hours Saved/Week:     {hours_saved / 4:.0f} hours")

    print("\n  CATEGORY BREAKDOWN")
    breakdown = metrics.get("category_breakdown", {})
    if breakdown:
        for category, count in breakdown.items():
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {category:<28} {count:>4} tickets  ({pct:.1f}%)")
    else:
        print("  No category data available yet.")

    print("\n" + "=" * 60)
    print("  Datawebify — Enterprise AI Automation")
    print("  datawebify.com  |  support.datawebify.com")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    print("Fetching live metrics from support.datawebify.com...")
    metrics = fetch_metrics()
    health = fetch_health()
    print_business_report(metrics, health)