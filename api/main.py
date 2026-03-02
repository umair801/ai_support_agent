import logging
import os
import sys
from datetime import datetime, timezone
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.orchestrator import run_pipeline
from core.export import save_ticket, fetch_all_tickets, export_to_csv
from core.config import ProcessedTicket, TicketInput
from agents.metrics_agent import calculate_metrics

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AgAI-3 Enterprise Support Agent",
    description="Autonomous AI customer support system — 60-70% auto-resolution rate, under 30s response time.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# --- Request Models ---
class TicketRequest(BaseModel):
    customer_email: str
    customer_name: Optional[str] = None
    subject: str
    body: str


# --- Health Check ---
@app.get("/health")
def health_check():
    return {
        "status": "online",
        "project": "AgAI-3 AI Support Agent",
        "timestamp": datetime.now(tz=timezone.utc).isoformat()
    }


# --- Submit Ticket (Webhook / API) ---
@app.post("/tickets/submit")
def submit_ticket(request: TicketRequest):
    try:
        logger.info(f"Incoming ticket from {request.customer_email}: {request.subject}")

        result = run_pipeline(request.model_dump())

        processed_dict = result.get("processed_ticket")
        if not processed_dict:
            raise HTTPException(status_code=500, detail="Pipeline failed to process ticket")

        processed = ProcessedTicket(**processed_dict)
        saved = save_ticket(processed)

        return {
            "success": True,
            "ticket_id": saved.get("id"),
            "status": processed.status,
            "category": processed.category,
            "urgency": processed.urgency,
            "complexity": processed.complexity,
            "confidence_score": processed.confidence_score,
            "response_time_seconds": processed.response_time_seconds,
            "ai_response": processed.ai_response if processed.status == "auto_resolved" else None,
            "escalation_reason": processed.escalation_reason if processed.status == "escalated" else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ticket submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Get All Tickets ---
@app.get("/tickets")
def get_tickets(
    status: Optional[str] = Query(None, description="Filter by status: auto_resolved, escalated, pending"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, le=200)
):
    try:
        tickets = fetch_all_tickets()

        if status:
            tickets = [t for t in tickets if t.get("status") == status]
        if category:
            tickets = [t for t in tickets if t.get("category") == category]

        return {
            "total": len(tickets),
            "tickets": tickets[:limit]
        }

    except Exception as e:
        logger.error(f"Failed to fetch tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Get Metrics ---
@app.get("/metrics")
def get_metrics():
    try:
        raw_tickets = fetch_all_tickets()

        if not raw_tickets:
            return {"message": "No tickets found", "metrics": {}}

        processed_tickets = []
        for t in raw_tickets:
            try:
                processed_tickets.append(ProcessedTicket(
                    customer_email=t.get("customer_email", ""),
                    customer_name=t.get("customer_name"),
                    subject=t.get("subject", ""),
                    body=t.get("body", ""),
                    category=t.get("category", "other"),
                    urgency=t.get("urgency", 1),
                    complexity=t.get("complexity", "simple"),
                    confidence_score=t.get("confidence_score", 0.0),
                    status=t.get("status", "pending"),
                    ai_response=t.get("ai_response"),
                    escalation_reason=t.get("escalation_reason"),
                    response_time_seconds=t.get("response_time_seconds")
                ))
            except Exception:
                continue

        metrics = calculate_metrics(processed_tickets)
        return {"metrics": metrics}

    except Exception as e:
        logger.error(f"Failed to calculate metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Export CSV ---
@app.get("/export/csv")
def export_csv():
    try:
        path = export_to_csv()
        if not path:
            raise HTTPException(status_code=404, detail="No tickets to export")
        return {"success": True, "exported_to": path}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Get Single Ticket by ID ---
@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    try:
        from core.database import get_supabase_client
        client = get_supabase_client()
        response = client.table("tickets").select("*").eq("id", ticket_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Ticket not found")

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch ticket {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)