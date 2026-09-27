# BusiAI — AI Decision Engine for Business Data

> **From data to decisions. With proof.**

BusiAI is an evidence-first AI business intelligence platform. Upload any business dataset, ask questions in plain English, and get insights backed by verifiable calculations — not hallucinations. Every number is computed deterministically by DuckDB and Python; the LLM only decides *what* to analyze, never *what the answer is*.

---

## Features

| Feature | Description |
|---|---|
| **Auto Insights** | Automatically surface trend shifts, concentration risks, anomalies, and outliers the moment data is ingested |
| **AI Investigation Console** | Ask free-form business questions; the engine generates hypotheses, runs SQL queries, and returns a grounded evidence package |
| **Evidence Layer** | Every finding includes the exact SQL query executed, raw data points, calculation proof, and confidence score |
| **What-If Simulator** | Parametric scenario modelling with price elasticity, churn dynamics, and conversion levers — with 3-band projections (conservative / base / optimistic) |
| **Decision Graph** | Visual cause-and-effect reasoning chain from question → evidence → action |
| **SQL Workbench** | Direct DuckDB query interface against any ingested dataset |
| **Dataset Profiler** | Automatic column-type detection, null analysis, statistical distributions, cardinality, and outlier scoring |
| **Zero-hallucination guarantee** | All numeric outputs are computed by DuckDB; LLM outputs are validated against actual data before being shown |

---

## Architecture

```
Upload (CSV/Excel)
    │
    ▼
Ingestion Service ──► DuckDB (in-process)
    │
    ▼
Profiling Service ──► Column types, null rates, key metrics, key dimensions
    │
    ▼
Auto-Insights Engine ──► Deterministic trend / anomaly / concentration detection
    │
    ▼
AI Investigation ──► LLM generates hypotheses ──► DuckDB validates each one
    │
    ▼
Evidence Package ──► SQL proofs + calculation audit trail
    │
    ▼
Recommendations + Decision Graph + What-If Simulator
    │
    ▼
Next.js Dashboard (minimalist white/blue UI)
```

**Core design rule:** The LLM decides *what* to analyze. DuckDB + Python decide *what the numbers are*. Results are never surfaced unless they are mathematically verified.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16 (App Router), React 19, TypeScript 5, Tailwind CSS 4, Recharts 3, Lucide React |
| **Backend** | Python 3.12+, FastAPI 0.115+, Pydantic v2, Uvicorn |
| **Database** | DuckDB 1.0+ (in-process analytical engine) |
| **Data Processing** | Pandas 2.2+, NumPy 1.26+, SciPy 1.13+ |
| **AI / LLM** | Groq (`openai/gpt-oss-120b`) with Gemini failover — falls back to deterministic rule engine if no key is set |
| **File Formats** | CSV, Excel (`.xlsx`, `.xls`, multi-sheet) |

---

## Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 18+** and **npm**
- A Groq API key and optionally a Gemini API key for failover *(the app remains functional without either using the deterministic fallback)*

---

### 1. Clone & Configure

```bash
git clone <repo-url>
cd busiai
cp .env.example .env
# Open .env and add your GROQ_API_KEY if you have one
```

---

### 2. Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn app.main:app --reload --port 8000
```

Backend will be live at **http://localhost:8000**

---

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be live at **http://localhost:3000**

---

### 4. Verify

| Endpoint | Expected |
|---|---|
| `http://localhost:3000` | Dashboard UI |
| `http://localhost:8000/health` | `{"status": "healthy"}` |
| `http://localhost:8000/docs` | FastAPI Swagger UI |

On first load, the app automatically ingests a sample SaaS MRR dataset so you can explore all features immediately — no manual upload required.

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# LLM Provider: Groq primary, Gemini fallback
LLM_PROVIDER=groq
GROQ_MODEL=openai/gpt-oss-120b
GEMINI_MODEL=gemini-3.8-flash

# API Keys — Gemini is used automatically if a Groq request fails
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Storage
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=50

# Limits
QUERY_TIMEOUT_SECONDS=30
MAX_RESULT_ROWS=10000
```

> **Note:** BusiAI works fully offline without any API key. The deterministic reasoning engine handles profiling, insights, and simulation automatically. The LLM layer is only used for free-form question answering in the Investigation Console.

---

## API Reference

Base URL: `http://localhost:8000/api/v1`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/datasets` | List all ingested datasets |
| `POST` | `/datasets/upload` | Upload a CSV or Excel file |
| `GET` | `/profile/{dataset_id}` | Statistical profile of a dataset |
| `GET` | `/insights/{dataset_id}` | Auto-generated business insights |
| `POST` | `/investigation/run` | Run an AI-powered investigation |
| `POST` | `/graph/build` | Build a decision reasoning graph |
| `POST` | `/simulation/run` | Run a What-If scenario simulation |
| `POST` | `/analysis/query` | Execute a raw DuckDB SQL query |

Full interactive docs available at `http://localhost:8000/docs`.

---

## Project Structure

```
busiai/
├── frontend/                   # Next.js 16 App
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Main dashboard (tabs: overview/investigate/graph/simulator/profile/workbench)
│   │   └── globals.css         # Design tokens + utility classes
│   ├── components/
│   │   ├── Navbar.tsx          # Top navigation + dataset switcher
│   │   ├── DatasetUploader.tsx # File upload modal (drag-and-drop)
│   │   ├── AutoInsightsDeck.tsx        # Insight cards with severity badges
│   │   ├── AIInvestigationConsole.tsx  # Free-form question → evidence UI
│   │   ├── EvidenceModal.tsx           # SQL proof + data inspector
│   │   ├── DecisionGraphView.tsx       # Causal reasoning graph
│   │   ├── WhatIfSimulator.tsx         # Scenario sliders + projection chart
│   │   ├── DatasetProfileView.tsx      # Column stats explorer
│   │   └── SQLWorkbench.tsx            # Raw DuckDB query runner
│   └── lib/
│       └── api.ts              # Typed API client (all backend calls)
│
├── backend/                    # FastAPI Application
│   ├── app/
│   │   ├── main.py             # App entry point + CORS middleware
│   │   ├── core/
│   │   │   ├── config.py       # Settings (pydantic-settings)
│   │   │   └── database.py     # DuckDB connection manager
│   │   ├── api/v1/router.py    # API route aggregator
│   │   ├── ingestion/          # File parsing + DuckDB table registration
│   │   ├── profiling/          # Column typing + statistical analysis
│   │   ├── analysis/           # Auto-insights engine + SQL execution
│   │   ├── investigation/      # Hypothesis generation + evidence assembly
│   │   ├── evidence/           # Evidence item construction + SQL proof
│   │   ├── simulation/         # What-If parametric model
│   │   ├── recommendations/    # Action recommendation engine
│   │   ├── graph/              # Decision graph builder
│   │   ├── query/              # Safe DuckDB query execution
│   │   └── llm/
│   │       └── provider.py     # LLM abstraction (Groq / Gemini failover / Deterministic)
│   ├── requirements.txt
│   └── tests/
│
├── sample_data/
│   ├── saas_monthly_metrics.csv    # SaaS MRR / churn / CAC / LTV demo data
│   └── ecommerce_orders.csv        # E-commerce orders demo data
│
└── .env.example                # Environment variable template
```

---

## How It Works

### Data Ingestion
Upload a CSV or Excel file. The ingestion service sanitizes column names, infers data types, registers the data as a DuckDB in-memory table, and extracts metadata (row count, column count, sample values).

### Auto Profiling
The profiling service classifies every column as `numeric`, `categorical`, `datetime`, or `boolean`. It computes null rates, IQR-based outlier counts, cardinality ratios, top-value distributions, and identifies key metrics and dimensions automatically.

### Auto Insights
The insights engine runs a battery of deterministic SQL queries to find: period-over-period metric changes, Pareto concentration (top-N account for X%), segment divergence, anomalous spikes or drops, and data quality issues — all without requiring an API key.

### AI Investigation
When you ask a question, the LLM generates a set of hypotheses to test (e.g., *"August churn spike was driven by EMEA Starter plan"*). Each hypothesis is validated by executing a specific DuckDB query against your actual data. The result is confirmed, refuted, or marked inconclusive — with the SQL proof included.

### What-If Simulation
The simulation engine applies parametric multipliers (price elasticity −0.3 demand curve, churn lifetime value compounding, conversion rate linear scaling) to your dataset's baseline metric, then projects a 6-month forward curve with conservative (65%), base (100%), and optimistic (135%) scenario bounds.

---

## What's Next

While BusiAI currently provides robust in-memory analysis for CSV and Excel files, here are the key features planned for future releases:

* **Live Data Warehouse Connectors:** Direct, read-only integration with PostgreSQL, BigQuery, and Snowflake so teams can query live production data without exporting files.
* **Automated Anomaly Alerts:** Scheduled background scans that notify teams via Slack or email when core metrics deviate beyond historical bounds.
* **Executive PDF & Slide Deck Export:** One-click exports of investigation summaries, decision graphs, and simulation scenarios for leadership presentations.
* **Multi-Table Relational Analysis:** Automated join detection to investigate complex business models spanning multiple related tables.

---

## Contributing

Contributions, bug reports, and feature requests are welcome! Feel free to open an issue or submit a pull request.

---

## License

MIT
