# Self-Healing RAG — Starter Kit

A staged, beginner-friendly implementation of a RAG-based auto-remediation
system for IT/infra incidents. Build it stage by stage — don't skip to
auto-execution before retrieval is solid.

## Folder structure

```
self-healing-rag/
├── data/
│   └── incidents/        # Your knowledge base: past incident records (JSON)
├── src/
│   ├── ingest.py          # Stage 1-2: load incidents into vector DB
│   ├── retrieve.py        # Stage 2: query the vector DB
│   ├── diagnose.py        # Stage 3: LLM diagnosis using retrieved context
│   ├── alert_server.py    # Stage 4: webhook receiver (FastAPI)
│   ├── actions.py         # Stage 5: safe pre-approved remediation actions
│   ├── executor.py        # Stage 5: tiered auto-execution logic
│   └── feedback.py        # Stage 6: log outcomes back into knowledge base
├── scripts/
│   └── test_query.py      # Quick manual test of retrieval + diagnosis
├── requirements.txt
└── .env.example
```

## Setup

```bash
cd self-healing-rag
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # add your ANTHROPIC_API_KEY
```

## Build order (do these in sequence)

1. **Fill `data/incidents/`** with 10-20 real past incidents (templates included).
   This matters more than any code — see `data/incidents/_TEMPLATE.json`.

2. **Stage 1-2 — Ingest + retrieve**
   ```bash
   python src/ingest.py
   python scripts/test_query.py "payment-service pod keeps restarting, memory error"
   ```
   Confirm it retrieves the right past incident before moving on.

3. **Stage 3 — Diagnosis**
   `scripts/test_query.py` already chains retrieval → LLM diagnosis. Read the
   output carefully. Tune `data/incidents/` wording if retrieval is off —
   fix the data before touching the code.

4. **Stage 4 — Connect real alerts**
   ```bash
   uvicorn src.alert_server:app --reload --port 8000
   ```
   Point your alerting tool's webhook (Prometheus Alertmanager, Datadog,
   CloudWatch→SNS→Lambda, etc.) at `POST /alert`. Edit `normalize_alert()` in
   `alert_server.py` to match your alert's payload shape. By default this
   stage only posts a suggested diagnosis to Slack/console — it does NOT
   execute anything. Run this for a few weeks with human review before
   moving to Stage 5.

5. **Stage 5 — Tiered auto-execution**
   Edit `src/actions.py` to wire `SAFE_ACTIONS` to your real automation
   (kubectl, Ansible, AWS SSM, etc.). Only low-risk, pre-approved actions
   should ever auto-execute — everything else routes to a human via
   `executor.py`.

6. **Stage 6 — Feedback loop**
   `src/feedback.py` writes the outcome of each fix back into
   `data/incidents/` as a new record, so the knowledge base grows over time.
   Re-run `src/ingest.py` periodically (or on a schedule) to re-index.

## Notes on safety

- Never let the LLM generate raw shell/SQL commands for execution. It should
  only ever select from `SAFE_ACTIONS` — a fixed, human-reviewed allow-list.
- Always define a rollback step before any action is added to `SAFE_ACTIONS`.
- Keep a human-approval path (Slack button, ticket, etc.) for anything
  outside the allow-list or above your risk threshold.
