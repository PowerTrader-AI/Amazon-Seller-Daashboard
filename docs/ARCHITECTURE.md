# Enterprise Sourcing Engine Architecture

## Goals
- Automate weekly sourcing (Top 5) in <2 hours/week.
- Support user-selected categories.
- Secure, confidential data flow.
- AI-assisted decision summaries.

## Core Services
1. **API Service (FastAPI)**
   - Endpoints: `/categories`, `/run`, `/top5`, `/explain/{asin}`
   - Runs Keepa Product Finder, scoring, and persistence.

2. **Worker / Scheduler**
   - GitHub Actions weekly schedule (Friday night UTC).
   - Optional: Add a worker queue for larger scans.

3. **Database (PostgreSQL on Railway)**
   - Stores historical BSR, price, and scores.

4. **Frontend (Next.js recommended)**
   - Enterprise dashboard: category selection, Top 5, trends.

## AI Features
- Score explanation and decision summary (rule-based now, LLM-ready later).
- Risk tags: volatility, competition, trend slope.
- Optional future: LLM-generated reports for sourcing meetings.

## Security & Confidentiality
- Secrets stored in GitHub Secrets/Railway Variables.
- .env never committed.
- Minimal logging (no raw keys).

## Data Flow
1. User sets categories via API.
2. Weekly job runs `run_sourcing.py`.
3. Data stored in PostgreSQL.
4. Dashboard reads Top 5 and explanations.

## Next Enhancements
- Add job queue (Redis + RQ/Celery).
- Add category discovery endpoint.
- Add price/BSR trend visualizations.
- Add role-based access control.
