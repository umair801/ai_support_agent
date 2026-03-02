import logging
import os
import sys
import time
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.config import (
    TicketInput,
    ClassifiedTicket,
    ProcessedTicket,
    MIN_CONFIDENCE_FOR_AUTO_RESOLVE,
    ALWAYS_ESCALATE_CATEGORIES
)
from agents.classification_agent import classify_ticket
from agents.response_agent import generate_response
from agents.escalation_agent import escalate_ticket
from agents.metrics_agent import calculate_metrics

load_dotenv()
logger = logging.getLogger(__name__)


# --- LangGraph State ---
class AgentState(TypedDict):
    ticket_input: dict
    classified_ticket: dict | None
    processed_ticket: dict | None
    metrics: dict | None
    error: str | None


# --- Node: Classify ---
def classify_node(state: AgentState) -> AgentState:
    try:
        ticket = TicketInput(**state["ticket_input"])
        classified = classify_ticket(ticket)
        state["classified_ticket"] = classified.model_dump()
        logger.info(f"Classified: {classified.category} | Urgency: {classified.urgency} | Complexity: {classified.complexity}")
    except Exception as e:
        state["error"] = f"Classification failed: {e}"
        logger.error(state["error"])
    return state


# --- Node: Auto-Resolve ---
def response_node(state: AgentState) -> AgentState:
    try:
        classified = ClassifiedTicket(**state["classified_ticket"])
        processed = generate_response(classified)
        state["processed_ticket"] = processed.model_dump()
        logger.info(f"Auto-resolved ticket for {processed.customer_email}")
    except Exception as e:
        state["error"] = f"Response generation failed: {e}"
        logger.error(state["error"])
    return state


# --- Node: Escalate ---
def escalation_node(state: AgentState) -> AgentState:
    try:
        classified = ClassifiedTicket(**state["classified_ticket"])
        processed = escalate_ticket(classified)
        state["processed_ticket"] = processed.model_dump()
        logger.info(f"Escalated ticket for {processed.customer_email}")
    except Exception as e:
        state["error"] = f"Escalation failed: {e}"
        logger.error(state["error"])
    return state


# --- Node: Metrics ---
def metrics_node(state: AgentState) -> AgentState:
    try:
        if state.get("processed_ticket"):
            processed = ProcessedTicket(**state["processed_ticket"])
            metrics = calculate_metrics([processed])
            state["metrics"] = metrics
            logger.info(f"Metrics calculated: {metrics.get('auto_resolution_rate_pct')}% auto-resolution")
    except Exception as e:
        state["error"] = f"Metrics failed: {e}"
        logger.error(state["error"])
    return state


# --- Routing Logic ---
def route_ticket(state: AgentState) -> str:
    if state.get("error"):
        return "escalate"

    classified = state.get("classified_ticket", {})
    complexity = classified.get("complexity")
    confidence = classified.get("confidence_score", 0)
    category = classified.get("category", "")
    urgency = classified.get("urgency", 1)

    if (
        complexity == "complex"
        or confidence < MIN_CONFIDENCE_FOR_AUTO_RESOLVE
        or category in ALWAYS_ESCALATE_CATEGORIES
        or urgency >= 4
    ):
        logger.info("Routing to escalation")
        return "escalate"

    logger.info("Routing to auto-resolve")
    return "resolve"


# --- Build Graph ---
def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("classify", classify_node)
    graph.add_node("resolve", response_node)
    graph.add_node("escalate", escalation_node)
    graph.add_node("metrics_node", metrics_node)

    graph.set_entry_point("classify")

    graph.add_conditional_edges(
        "classify",
        route_ticket,
        {
            "resolve": "resolve",
            "escalate": "escalate"
        }
    )

    graph.add_edge("resolve", "metrics_node")
    graph.add_edge("escalate", "metrics_node")
    graph.add_edge("metrics_node", END)

    return graph.compile()


# --- Run Pipeline ---
def run_pipeline(ticket_data: dict) -> dict:
    graph = build_graph()

    initial_state: AgentState = {
        "ticket_input": ticket_data,
        "classified_ticket": None,
        "processed_ticket": None,
        "metrics": None,
        "error": None
    }

    result = graph.invoke(initial_state)
    return result


if __name__ == "__main__":
    simple_ticket = {
        "customer_email": "john.smith@company.com",
        "customer_name": "John Smith",
        "subject": "How do I export my data to CSV?",
        "body": "Hi, I have been trying to export my account data to CSV but cannot find the option. Can you help?"
    }

    complex_ticket = {
        "customer_email": "sarah.johnson@enterprise.com",
        "customer_name": "Sarah Johnson",
        "subject": "Unauthorized charges — considering legal action",
        "body": "I have been charged three times for a subscription I cancelled. I want a full refund immediately or I will escalate legally."
    }

    for label, ticket in [("SIMPLE", simple_ticket), ("COMPLEX", complex_ticket)]:
        print(f"\n{'='*50}")
        print(f"TESTING: {label} TICKET")
        print("="*50)
        result = run_pipeline(ticket)
        processed = result.get("processed_ticket", {})
        print(f"Status:           {processed.get('status')}")
        print(f"Category:         {processed.get('category')}")
        print(f"Urgency:          {processed.get('urgency')}/5")
        print(f"Complexity:       {processed.get('complexity')}")
        print(f"Confidence:       {processed.get('confidence_score')}")
        print(f"Response Time:    {processed.get('response_time_seconds')}s")
        if processed.get("status") == "auto_resolved":
            print(f"\nAI Response:\n{processed.get('ai_response')}")
        else:
            print(f"\nEscalation Reason: {processed.get('escalation_reason')}")
            print(f"Context Summary:   {processed.get('ai_response')}")