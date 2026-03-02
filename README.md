# AgAI-3: Enterprise AI Customer Support Agent

> **Portfolio Project 3 of 50** | Agentic AI Specialist & Enterprise Consultant  
> Live at: [support.datawebify.com](https://support.datawebify.com)

---

## The Problem

A 5-person enterprise support team handling 10,000 tickets per month costs between $8,000 and $15,000 per month in salaries alone — before factoring in training, turnover, or overtime during peak periods. The majority of those tickets are repetitive tier-1 queries that follow predictable patterns. Yet every ticket goes through the same expensive human workflow regardless of complexity.

The result: slow response times, inconsistent quality, and a team burned out on questions that do not require human judgment.

---

## The Solution

AgAI-3 is an autonomous multi-agent system that receives, classifies, resolves, and tracks support tickets without human intervention — for tickets that do not need it. Complex, sensitive, or high-urgency tickets are escalated immediately with full structured context so human agents can act fast.

**Business outcomes:**

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Auto-resolution rate | 0% | 60-70% | +65% |
| Average response time | 4-8 hours | Under 30 seconds | -99% |
| Cost per ticket (tier-1) | $1.50 | $0.02 | -99% |
| Agent hours saved | 0 | 100+ per week | +100 hrs |
| Monthly cost (est.) | $12,000 | $2,000-4,000 | -70% |

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

### Agent Breakdown

**Classification Agent** — Uses GPT-4o-mini to analyze each incoming ticket and assign a category, urgency level (1-5), complexity (simple/complex), and a confidence score. This score drives all downstream routing decisions.

**Response Agent** — For simple tickets, generates a personalized, professional email response using ticket content and category context. Targets under 30 seconds from receipt to reply.

**Escalation Agent** — For complex or high-urgency tickets, prepares a structured handoff brief for the human agent — including the issue summary, escalation reason, and recommended first action. No context is lost in the transfer.

**Metrics Agent** — Tracks auto-resolution rate, escalation rate, average response time, urgency distribution, and estimated cost savings across all processed tickets.

**LangGraph Orchestrator** — Connects all agents into a single conditional workflow. Classifies first, then routes to either auto-resolve or escalation based on complexity, urgency, category, and confidence score.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Agent Framework | LangGraph |
| AI Model | OpenAI GPT-4o-mini |
| API Layer | FastAPI + Uvicorn |
| Database | Supabase (PostgreSQL) |
| Data Models | Pydantic v2 |
| Deployment | Docker + Railway |
| Language | Python 3.12 |
| Other | pandas, httpx, python-dotenv |

---

## Project Structure

```
AgAI_3_AI_Support_Agent/
├── agents/
│   ├── classification_agent.py   # GPT-4o-mini ticket classifier
│   ├── response_agent.py         # AI response generator
│   ├── escalation_agent.py       # Human handoff agent
│   └── metrics_agent.py          # Performance tracker
├── core/
│   ├── config.py                 # Categories, urgency levels, Pydantic models
│   ├── database.py               # Supabase client
│   ├── orchestrator.py           # LangGraph workflow
│   └── export.py                 # Supabase save + CSV export
├── api/
│   └── main.py                   # FastAPI endpoints
├── exports/                      # CSV export output
├── logs/                         # Structured logging
├── .env                          # Environment variables (not committed)
├── Dockerfile
├── railway.json
└── requirements.txt
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System status check |
| POST | `/tickets/submit` | Submit a ticket for processing |
| GET | `/tickets` | Retrieve all tickets (filterable) |
| GET | `/tickets/{id}` | Get a single ticket by ID |
| GET | `/metrics` | Live business metrics dashboard |
| GET | `/export/csv` | Export all ticket data to CSV |

### Submit a Ticket

```bash
curl -X POST https://support.datawebify.com/tickets/submit \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "client@company.com",
    "customer_name": "Jane Smith",
    "subject": "Cannot access my account",
    "body": "I reset my password but still cannot log in. Need access urgently."
  }'
```

**Response:**

```json
{
  "success": true,
  "ticket_id": "uuid-here",
  "status": "auto_resolved",
  "category": "account_access",
  "urgency": 3,
  "complexity": "simple",
  "confidence_score": 0.94,
  "response_time_seconds": 14.7,
  "ai_response": "Hi Jane, I understand you're having trouble accessing your account..."
}
```

---

## Routing Logic

A ticket is escalated to a human agent when any of the following conditions are met:

- Urgency is 4 or 5 (high / critical)
- Category is `complaint` or `refund_request`
- Confidence score falls below 0.75
- Complexity is marked `complex` by the classifier

All other tickets are auto-resolved with a personalized AI response.

---

## Ticket Categories

`billing` | `technical_support` | `account_access` | `product_question` | `refund_request` | `shipping` | `complaint` | `other`

---

## Local Setup

```bash
# Clone the repository
git clone https://github.com/umair801/ai-support-agent.git
cd ai-support-agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY

# Run the API
python api/main.py
```

Visit `http://localhost:8000/docs` for the interactive API documentation.

---

## Docker Deployment

```bash
docker build -t agai3-support-agent .
docker run -p 8000:8000 --env-file .env agai3-support-agent
```

---

## Business Value

This system is designed for any business handling 1,000+ support tickets per month — e-commerce companies, SaaS platforms, and enterprise software vendors. At 10,000 tickets per month, a 65% auto-resolution rate eliminates 6,500 manual responses. At $1.50 per human-handled ticket, that is $9,750 in monthly savings against an AI processing cost of approximately $130.

**ROI: 75x return on AI processing costs.**

Typical engagement value for implementation and customization: **$15,000 to $40,000**.

---

## Related Projects

- **AgAI-1:** Enterprise WhatsApp Automation — [whatsapp.datawebify.com](https://whatsapp.datawebify.com)
- **AgAI-2:** B2B Lead Generation System — [leads.datawebify.com](https://leads.datawebify.com)
- **AgAI-3:** This project — [support.datawebify.com](https://support.datawebify.com)

---

## Contact

**Muhammad Umair**  
Agentic AI Specialist & Enterprise Consultant  
[datawebify.com](https://datawebify.com) | [github.com/umair801](https://github.com/umair801)
