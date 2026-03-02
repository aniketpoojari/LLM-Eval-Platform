# LLM Evaluation & Red-Teaming Platform

![Python](https://img.shields.io/badge/python-3670AD?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

A general-purpose platform to evaluate, red-team, and A/B test any LLM-powered application. Features multi-dimension evaluation (LLM-as-judge), automated red-teaming with 216 adversarial attacks, A/B testing with statistical significance, and observability dashboards.

## Architecture

```
React Frontend (Vite + TailwindCSS)
         |
    REST API
         |
FastAPI Backend
  |-- Evaluation Engine (LLM-as-Judge, 5 dimensions)
  |-- Red-Team Engine (216 attacks, 6 categories)
  |-- A/B Testing (paired t-test, bootstrap CI)
  |-- Observability (tokens, latency, cost tracking)
  |-- Target Service (HTTP client -> any LLM app)
         |
    SQLite (9 tables)
```

## Screenshots

### Dashboard Overview
![Dashboard Overview](images/dashboard.png)

### Configure Targets
![Configure Targets](images/configure_targets.png)

### Evaluation Results
![Evaluation Results](images/evaluation_result.png)

### Red-Team Security Analysis
![Red-Team Security Analysis](images/red_team_result.png)

### Observability Dashboard
![Observability Dashboard](images/observability.png)

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Dimension Eval** | Score responses on factuality, relevance, coherence, safety, helpfulness |
| **LLM-as-Judge** | Groq-powered judge with structured prompts per dimension |
| **Red-Teaming** | 216 built-in attacks across 6 categories (injection, jailbreak, PII, bias, harmful, hallucination) |
| **A/B Testing** | Paired comparison with scipy statistical tests (t-test, bootstrap CI, effect size) |
| **Observability** | Token usage, latency, cost tracking, score trends |
| **General-Purpose** | Works against ANY target API via configurable HTTP client |
| **Real-time Progress** | SSE streaming for long-running evaluations |
| **Export** | CSV/JSON export of evaluation results |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI |
| Judge LLM | Groq (Llama 3.1 8B) |
| Frontend | React 18 + Vite + TailwindCSS |
| Charts | Recharts |
| State | TanStack Query |
| Statistics | scipy (paired t-test, bootstrap) |
| Database | SQLite |
| Deploy | Docker (multi-stage) |

## Quick Start

```bash
# Clone
git clone https://github.com/aniketpoojari/LLM-Eval-Platform.git
cd LLM-Eval-Platform

# --- Backend Setup ---
# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Start FastAPI backend (Port 8888)
uvicorn backend.main:app --host 0.0.0.0 --port 8888 --reload

# --- Frontend Setup ---
# (In a separate terminal)
cd frontend
npm install
npm run dev
```

## Docker

```bash
docker-compose up --build
```

Access: UI at `http://localhost:8888`, API at `http://localhost:8888/api`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST/GET | `/api/targets` | CRUD for target LLM apps |
| POST | `/api/targets/{id}/test` | Test target connectivity |
| POST | `/api/evaluations` | Create + start evaluation |
| GET | `/api/evaluations/{id}/results` | Get evaluation results |
| GET | `/api/evaluations/{id}/progress` | SSE progress stream |
| GET | `/api/evaluations/{id}/export` | Export results (CSV/JSON) |
| POST | `/api/red-team/runs` | Start red-team run |
| GET | `/api/red-team/attacks` | Browse attack library |
| GET | `/api/red-team/categories` | Attack category taxonomy |
| POST | `/api/ab-tests` | Create A/B experiment |
| GET | `/api/ab-tests/{id}/stats` | Statistical analysis |
| GET | `/api/observability/summary` | Overview metrics |
| GET | `/api/observability/tokens` | Token usage time-series |
| GET | `/api/observability/costs` | Cost tracking |
| GET | `/health` | Health check |

## Integration with Enterprise Assistant

The platform was successfully used to validate the **Enterprise AI Assistant (MCP)** project, resulting in several key improvements:
- **Bug Discovery**: Identified a critical agent workflow crash related to message formatting.
- **Security Hardening**: Detected a "Debug Mode" bypass vulnerability, leading to new guardrail regex patterns.
- **Performance Benchmarking**: Verified 5.0/5.0 factuality scores for complex e-commerce SQL queries.
- **Red-Teaming**: Improved safety scores from 0.47 to 0.72 by iteratively testing against built-in adversarial attacks.

## Red-Team Attack Categories

| Category | Attacks | Description |
|----------|---------|-------------|
| Prompt Injection | 40 | Override system instructions, role play, encoding bypass |
| Jailbreak | 40 | DAN variants, hypothetical scenarios, creative writing |
| PII Extraction | 32 | Direct requests, system prompt leak, data exfiltration |
| Bias Probing | 40 | Gender, racial, age, socioeconomic, religious bias |
| Harmful Content | 32 | Violence, illegal activity, misinformation, hate speech |
| Hallucination | 32 | Fake facts, numerical tricks, authority appeal, temporal confusion |

## Evaluation Dimensions

| Dimension | Description |
|-----------|-------------|
| Factuality | Accuracy of claims, absence of hallucinations |
| Relevance | How well the response addresses the query |
| Coherence | Logical structure and readability |
| Safety | Absence of harmful, biased, or inappropriate content |
| Helpfulness | Actionability and usefulness of the response |

## Testing

```bash
# Backend tests
pytest backend/tests/ -v

# Frontend build check
cd frontend && npm run build
```

## Project Structure

```
LLM-Eval-Platform/
├── backend/
│   ├── main.py                     # FastAPI app
│   ├── api/                        # Route handlers
│   ├── config/                     # YAML config + loader
│   ├── database/                   # SQLite schema (9 tables)
│   ├── evaluation/                 # Dimensions, judge prompts, scorers, batch runner
│   ├── red_team/                   # Attack library (216), categories, safety scorer
│   ├── ab_testing/                 # Statistics, experiment runner, comparator
│   ├── observability/              # Metrics collector, aggregator
│   ├── services/                   # Service layer (eval, red-team, A/B, cost, target)
│   ├── models/                     # Pydantic models + DB manager
│   ├── utils/                      # Config, model loader, HTTP client, export
│   ├── logger/                     # Logging setup
│   ├── tests/                      # pytest tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/                  # 7 pages (Dashboard, Evals, RedTeam, AB, Obs, Targets, Settings)
│   │   ├── components/             # Layout + common + feature components
│   │   ├── api/                    # Axios API modules
│   │   ├── hooks/                  # Custom React hooks
│   │   └── utils/                  # Formatters, constants
│   ├── package.json
│   └── vite.config.js
├── Dockerfile                      # Multi-stage (Node + Python)
├── docker-compose.yaml
├── README.md
└── SYSTEM_DESIGN.md
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for judge LLM |
| `MODEL_NAME` | No | Judge model (default: llama-3.1-8b-instant) |
| `MODEL_PROVIDER` | No | LLM provider (default: groq) |
| `LOG_LEVEL` | No | Logging level (default: INFO) |

## License

MIT
