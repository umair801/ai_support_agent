# Enterprise AI Customer Support Agent

**Live Demo:** [support.datawebify.com](https://support.datawebify.com)  
**API Docs:** [support.datawebify.com/docs](https://support.datawebify.com/docs)  
**Project Page:** [datawebify.com/projects/agai3_ai_support_agent](https://datawebify.com/projects/agai3_ai_support_agent)  
**Portfolio:** [datawebify.com](https://datawebify.com) | Project 3 of 50

---

## The Problem

A 5-person support team handling 10,000 tickets per month costs $8,000–$15,000
monthly in salaries alone. Response times average 4–8 hours. Simple, repetitive
tickets consume the same human attention as complex, high-value ones. There is
no system to route the right ticket to the right handler automatically.

---

## The Solution

A fully autonomous, multi-agent AI system that classifies every incoming support
ticket, auto-resolves simple cases with personalized AI responses, and escalates
complex or sensitive cases to human agents with full structured context. The
entire pipeline runs in under 30 seconds per ticket.

---

## Business Impact

| Metric | Before | After | Change |
|---|---|---|---|
| Monthly support cost (10K tickets) | $12,000 | $2,800 | -77% |
| Average response time | 4–8 hours | Under 30 seconds | -99% |
| Tickets requiring human agents | 100% | 30–40% | -65% |
| Agent hours consumed per week | 250+ hours | 60–80 hours | -70% |
| Cost per ticket | $1.20 | $0.08–$0.36 | -80% |

**Target auto-resolution rate:** 60–70% of all Tier-1 tickets  
**Engagement value:** $15,000–$40,000 per deployment

---

## System Architecture
```
┌─────────────────────────────────────────────┐
│              Orchestrator Agent              │
│         (LangGraph — controls flow)          │
└──────┬──────────┬──────────┬────────────────┘
       │          │          │
       ▼          ▼          ▼
Classification  Response   Escalation
    Agent        Agent       Agent
 (category,   (generates  (routes to
  urgency,     AI reply)   human +
 complexity)               context)
       │          │          │
       └──────────┴──────────┘
                  │
                  ▼
           Metrics Agent
        (tracks resolution,
         response time, CSAT)
                  │
                  ▼
           Export Layer
      (Supabase + REST API)
```

### Agent Roles

**Classification Agent**
Receives each ticket and outputs: category, urgency score (1–5), complexity
label (simple or complex), and a confidence score. Powered by GPT-4o-mini with
structured JSON output.

**Response Agent**
Generates a personalized, context-aware reply for every auto-resolvable ticket.
Pulls customer history from Supabase to avoid generic responses.

**Escalation Agent**
Routes low-confidence or high-complexity tickets to human agents. Attaches a
structured context summary so the human never starts from scratch.

**Metrics Agent**
Tracks auto-resolution rate, average response time, escalation rate per
category, and cost per ticket in real time.

**Export Layer**
Persists every ticket and outcome to Supabase (PostgreSQL). Supports CSV export
for reporting.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Agent Framework | LangGraph |
| AI Model | OpenAI GPT-4o-mini |
| API Layer | FastAPI + Uvicorn |
| Database | Supabase (PostgreSQL) |
| Deployment | Docker + Railway |
| Data Validation | Pydantic v2 |
| HTTP Client | httpx |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ticket` | Submit a new support ticket |
| GET | `/tickets` | Retrieve all tickets |
| GET | `/tickets/{id}` | Retrieve a single ticket |
| GET | `/metrics` | Live business metrics |
| GET | `/export/csv` | Download ticket data as CSV |
| GET | `/health` | System health check |

**Full interactive docs:** [support.datawebify.com/docs](https://support.datawebify.com/docs)

---

## Quick Start (Local)
```bash
# 1. Clone the repository
git clone https://github.com/umair801/ai-support-agent.git
cd ai-support-agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Add your OPENAI_API_KEY and Supabase credentials to .env

# 5. Run the API
uvicorn main:app --reload

# 6. Open API docs
# http://localhost:8000/docs

# Production endpoints
# Live system:   https://support.datawebify.com
# API docs:      https://support.datawebify.com/docs
# Health check:  https://support.datawebify.com/health
# Metrics:       https://support.datawebify.com/metrics
# CSV export:    https://support.datawebify.com/export/csv
# Project page:  https://datawebify.com/projects/agai3_ai_support_agent
```

---

## Sample Ticket Request
```json
POST https://support.datawebify.com/ticket

{
  "customer_id": "cust_001",
  "customer_name": "Sarah Mitchell",
  "email": "sarah@example.com",
  "subject": "Cannot access my account",
  "body": "I have been locked out of my account for two days. 
           I tried resetting my password but never received the email.",
  "channel": "email"
}
```

**Response (auto-resolved in under 30 seconds):**
```json
{
  "ticket_id": "tkt_20240315_001",
  "status": "auto_resolved",
  "classification": {
    "category": "account_access",
    "urgency": 4,
    "complexity": "simple",
    "confidence": 0.94
  },
  "response": "Hi Sarah, I have located your account and triggered a 
               fresh password reset email...",
  "response_time_sec": 8.3,
  "metrics": {
    "auto_resolution_rate": 0.67,
    "avg_response_time_sec": 11.2
  }
}
```

---

## Project Structure
```
AgAI_3_AI_Support_Agent/
├── agents/
│   ├── classification_agent.py
│   ├── response_agent.py
│   ├── escalation_agent.py
│   └── metrics_agent.py
├── graph/
│   └── orchestrator.py
├── models/
│   └── ticket_models.py
├── export/
│   └── supabase_export.py
├── config/
│   └── ticket_config.py
├── main.py
├── metrics_report.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Deployment

The system is containerized with Docker and deployed on Railway with a custom
domain. Zero-downtime redeploys are handled automatically via Railway's Git
integration.

**Live system:** [support.datawebify.com](https://support.datawebify.com)

---

## Related Projects

| Project | Description | Live |
|---|---|---|
| Enterprise WhatsApp Automation | Autonomous WhatsApp outreach and response agent | [whatsapp.datawebify.com](https://whatsapp.datawebify.com) |
| B2B Lead Generation System | Multi-source lead enrichment and scoring agent | [leads.datawebify.com](https://leads.datawebify.com) |
| Enterprise AI Support Agent | This project | [support.datawebify.com](https://support.datawebify.com) |

---

## About Datawebify

Datawebify builds enterprise-grade Agentic AI systems for businesses handling
large-scale operations, support workflows, and data pipelines. Each system is
production-ready, fully documented, and built to deliver measurable ROI from
day one.

**Website:** [datawebify.com](https://datawebify.com)  
**Project Page:** [datawebify.com/projects/agai3_ai_support_agent](https://datawebify.com/projects/agai3_ai_support_agent)  
**Live System:** [support.datawebify.com](https://support.datawebify.com)  
**API Docs:** [support.datawebify.com/docs](https://support.datawebify.com/docs)  
**GitHub:** [github.com/umair801](https://github.com/umair801)