# System Design: LLM Evaluation & Red-Teaming Platform

## Overview

A general-purpose platform to evaluate any LLM-powered application. Supports multi-dimension evaluation (LLM-as-judge), automated red-teaming (216 adversarial attacks), A/B testing with statistical significance, and observability dashboards.

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                   React Frontend (Vite)                         │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌──────┐ ┌──────────┐ │
│  │Dashboard │ │ Evals    │ │Red Team │ │A/B   │ │Observ.   │ │
│  └──────────┘ └──────────┘ └─────────┘ └──────┘ └──────────┘ │
└──────────────────────┬─────────────────────────────────────────┘
                       │ REST API
┌──────────────────────▼─────────────────────────────────────────┐
│                   FastAPI Backend                               │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Evaluation   │  │  Red-Team    │  │  A/B Testing         │  │
│  │  Engine       │  │  Engine      │  │  Engine              │  │
│  │              │  │              │  │                      │  │
│  │ BatchRunner  │  │ AttackLib    │  │ ExperimentRunner     │  │
│  │ JudgeService │  │ SafetyScorer │  │ Statistics (scipy)   │  │
│  │ Dimensions   │  │ Generator    │  │ Comparator           │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│  ┌──────▼─────────────────▼──────────────────────▼───────────┐  │
│  │              Target Service (HTTP Client)                  │  │
│  │         Sends queries to ANY LLM application API           │  │
│  └──────────────────────┬────────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────▼────────────────────────────────────┐  │
│  │          Observability + Cost Tracking                     │  │
│  │    Metrics Collector → Aggregator → Time-series Queries    │  │
│  └──────────────────────┬────────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────▼────────────────────────────────────┐  │
│  │               Judge LLM (Groq / Llama 3.1 8B)             │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
               ┌──────────▼──────────┐
               │   SQLite Database    │
               │   (9 tables)         │
               └─────────────────────┘
```

## Design Decisions

### Why LLM-as-Judge?

- Scales to arbitrary dimensions without human labeling
- Each dimension has a structured prompt producing JSON {score, explanation}
- Consistent 1-5 Likert scale across all dimensions
- Groq provides fast, free-tier inference for judge calls

### Why 216 Built-in Attacks?

- Covers 6 categories: prompt injection, jailbreak, PII extraction, bias probing, harmful content, hallucination
- Each category has 4-8 subcategories with diverse attack vectors
- Attacks are curated from real-world adversarial research
- LLM-powered attack generator creates novel variations

### Why Paired Statistical Testing for A/B?

- Paired t-test controls for query difficulty (same query to both targets)
- Bootstrap confidence intervals for non-parametric robustness
- Cohen's d effect size quantifies practical significance
- Prevents false conclusions from random variation

### Why React + Vite Instead of Streamlit?

- Complex multi-page UI with interactive charts and real-time updates
- TanStack Query handles caching, polling, and optimistic updates
- Recharts provides publication-quality visualizations
- SSE progress tracking for long-running evaluations
- Production-grade frontend that demonstrates full-stack capability

### Robust Environment Configuration

The platform utilizes a strict environment loading strategy where `.env` file values explicitly override system environment variables (using `load_dotenv(override=True)`). This ensures total consistency across different execution environments and prevents accidental use of incorrect API keys.

### Target Service (Configurable HTTP Client)

The `HttpClient` utility is designed to be highly flexible, supporting:
- Custom request templates with `{{input}}` placeholders.
- Configurable JSON response path extraction.
- Dynamic header injection.
- Automatic retry logic for rate-limited (429) provider APIs.

## Data Flow

### Evaluation Pipeline
1. User creates evaluation → selects target, dimensions, queries
2. BatchRunner sends each query to target API
3. JudgeService scores response on each dimension
4. Results stored in SQLite with per-query breakdowns
5. Aggregate scores computed across all queries

### Red-Team Pipeline
1. User selects attack categories and max attacks
2. Attacks sampled from 216-item library
3. Each attack sent to target API
4. SafetyScorer (LLM-as-judge) evaluates safety of response
5. Results aggregated: overall safety score + category breakdown

### A/B Test Pipeline
1. User selects two targets and shared query set
2. Each query sent to both targets
3. JudgeService scores both responses on each dimension
4. Paired t-test determines statistical significance
5. Bootstrap CI provides confidence bounds

## Database Schema (9 tables)

| Table | Purpose |
|-------|---------|
| targets | LLM application configurations |
| evaluations | Batch evaluation runs |
| evaluation_results | Per-query evaluation scores |
| red_team_runs | Red-team execution runs |
| red_team_results | Per-attack results + safety scores |
| ab_experiments | A/B test experiments |
| ab_results | Paired comparison results |
| metrics | Observability time-series data |
| cost_tracking | Token usage and cost tracking |

## Key Files

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app with all routes |
| `backend/evaluation/batch_runner.py` | Evaluation orchestrator |
| `backend/evaluation/judge_prompts.py` | LLM-as-judge prompt templates |
| `backend/red_team/attack_library.py` | 216 adversarial attacks |
| `backend/red_team/safety_scorer.py` | LLM-based safety scoring |
| `backend/ab_testing/statistics.py` | Paired t-test, bootstrap CI, effect size |
| `backend/services/evaluation_service.py` | Evaluation service layer |
| `backend/services/red_team_service.py` | Red-team orchestration |
| `frontend/src/pages/Dashboard.jsx` | Overview dashboard |
| `frontend/src/pages/RedTeam.jsx` | Red-team execution UI |

## Deployment

### HuggingFace Spaces
- Docker SDK space (multi-stage build)
- Node.js builds React frontend → Python serves static files + API
- Auto-deployed via GitHub Actions on push to main

### CI/CD Pipeline
1. **Lint** - black, isort, flake8
2. **Backend Tests** - pytest (evaluation, red-team, A/B, API)
3. **Frontend Build** - npm build verification
4. **Docker Build** - build + health check
5. **Deploy** - Push to HuggingFace Spaces
