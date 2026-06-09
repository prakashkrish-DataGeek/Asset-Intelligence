# 🏭 Asset Intelligence Copilot

> **Chief AI Officer Pilot — Industrial AI Decision Support Console**  
> Model Context Protocol (MCP) for Large-Scale Asset Operations

---

## Executive Summary

Legacy operational data is **trapped value**. This pilot demonstrates how a AI can modernize industrial asset operations by connecting **legacy unstructured engineering knowledge** with **modern operational telemetry** through a clean, protocol-governed AI boundary.

When the system detects a pressure anomaly on **WELL-202B**, the AI agent:
1. Inspects real-time telemetry from the operational historian
2. Retrieves historical engineering context from the legacy document repository
3. Reads compliance and safety governance resources
4. Correlates the anomaly with documented integrity issues
5. Synthesizes a **mitigation recommendation** with full **evidence traceability**
6. Issues a **restart gate** verdict: permitted or prohibited, with explicit conditions

The entire system is **self-contained**, runs **locally**, and requires **no external cloud services**.

---

## What This Demonstrates

| Leadership Thesis | How the Pilot Proves It |
|---|---|
| **Legacy data is trapped value** | Unstructured 2018 integrity assessments and 2019 maintenance logs directly inform a 2026 operational decision |
| **MCP provides clean protocol boundaries** | The agent discovers tools and resources dynamically; the server can be swapped for production historians or SharePoint APIs without touching agent logic |
| **AI copilots must fuse telemetry + memory + safety** | Structured pressure readings, unstructured engineering narratives, and compliance frameworks are joined into a single evidence-based recommendation |
| **Narrow, high-value pilots prove time-to-insight** | From anomaly detection to mitigation recommendation in seconds, with full audit trail |
| **Explainability is non-negotiable in heavy industry** | Every tool call, document snippet, and compliance excerpt is cited; alternative hypotheses are surfaced |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT INDUSTRIAL OPERATIONS CONSOLE                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  TOP SUMMARY STRIP (persistent after run)                          │   │
│  │  Asset | Status | Severity | Confidence | Action | Restart | Time     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌──────────────┐  ┌──────────────────────────────────────────────────┐   │
│  │  SIDEBAR     │  │  MAIN WORKSPACE                                  │   │
│  │              │  │                                                  │   │
│  │  Asset       │  │  Title + Product Description                     │   │
│  │  Selector    │  │  Action Buttons (Demo / Diagnose / Clear)        │   │
│  │              │  │  ─────────────────────────────────────────────   │   │
│  │  Anomaly     │  │  AGENT EXECUTION TIMELINE (st.status blocks)     │   │
│  │  Watchlist   │  │  ─────────────────────────────────────────────   │   │
│  │              │  │  DECISION PANEL                                  │   │
│  │  Telemetry   │  │  • Current State                                 │   │
│  │  Preview     │  │  • Likely Root Cause                             │   │
│  │              │  │  • Alternative Considerations                    │   │
│  │  Legacy      │  │  • Recommended Mitigation                        │   │
│  │  Repository  │  │  • Safety & Compliance Note                      │   │
│  │  Browser     │  │  • Restart Conditions                            │   │
│  │              │  │  ─────────────────────────────────────────────   │   │
│  │  MCP Tools   │  │  EVIDENCE PACK (5 Tabs)                          │   │
│  │  & Resources │  │  • Telemetry | Risk | Legacy | Compliance | Trace│   │
│  │              │  │                                                  │   │
│  │  System      │  │  Each tab: source, timestamp, "Why It Mattered"  │   │
│  │  Health      │  │                                                  │   │
│  └──────────────┘  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              LOCAL MCP SERVER (JSON-RPC 2.0 semantics, in-process)         │
│  ┌────────────────────────────┐    ┌─────────────────────────────────────┐  │
│  │          TOOLS             │    │           RESOURCES                 │  │
│  │ • query_modern_telemetry   │    │ • compliance_framework.md           │  │
│  │ • query_risk_metrics       │    │ • WELL-202B_historical_integrity    │  │
│  │ • search_legacy_share      │    │   _2018.txt                         │  │
│  │ • list_legacy_documents    │    └─────────────────────────────────────┘  │
│  │ • query_maintenance_history│                                             │
│  └────────────────────────────┘                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌─────────────────────┐         ┌─────────────────────────┐
    │   SQLite Historian  │         │  Synthetic SharePoint   │
    │                     │         │  (Local Filesystem)     │
    │ • asset_telemetry   │         │                         │
    │ • risk_metrics      │         │ • Integrity assessments │
    │ • maintenance_events│         │ • Compliance memos      │
    └─────────────────────┘         │ • Operational handovers │
                                    └─────────────────────────┘
```

---

## Project Structure

```
asset-intelligence-copilot/
├── README.md                              # This file
├── requirements.txt                       # Python dependencies
├── .gitignore                             # Git ignore rules
├── app.py                                 # Streamlit dashboard (industrial console UI)
├── src/
│   ├── __init__.py
│   ├── config.py                          # Central configuration, paths, thresholds
│   ├── data_generator.py                  # Synthetic data bootstrap (SQLite + SharePoint)
│   ├── mcp_protocol.py                    # JSON-RPC 2.0 MCP message definitions
│   ├── mcp_server.py                      # Local MCP server (tools + resources)
│   └── mcp_client.py                      # ReAct agent + deterministic synthesis engine
├── synthetic_sharepoint/                  # Simulated legacy document repository
│   ├── WELL-202B_historical_integrity_2018.txt
│   ├── WELL-101A_production_handover_2021.md
│   ├── PLT-001_turnaround_report_2023.txt
│   ├── WELL-303C_drilling_completion_notes_2020.md
│   ├── general_ops_memo_pressure_management_2019.txt
│   └── compliance_framework.md
└── data/
    └── asset_ops.db                       # Auto-generated SQLite operations database
```

---

## Setup & Run

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/prakashkrish-DataGeek/asset-intelligence-copilot.git
cd asset-intelligence-copilot

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`.

### Run the Executive Demo

Click **Run Executive Demo** to execute the full ReAct agent loop with the pre-loaded scenario:

> *"We are seeing a critical pressure drop alert on asset WELL-202B right now. Check current telemetry and risk metrics, cross-reference historical engineering logs in SharePoint, review relevant compliance guidance, and provide the most likely root cause plus a recommended mitigation strategy with supporting evidence."*

---

## Business Scenario

### Asset: WELL-202B

**Current Condition (Real-Time Telemetry):**
- Pressure: **1,017 PSI** — below the 1,100 PSI safety threshold
- Status: **ANOMALY**
- Trend: **DROPPING** (~428 PSI decline over 6 hours)
- Risk Score: **88.7** (elevated)
- Integrity Flag: **COMPROMISED**
- Production Impact: **HIGH**

**Historical Context (Legacy Document, 2018):**
- Known history of **micro-fracturing in the lower shoe layer**
- Risk increases materially when pressure drops below **1,100 PSI**
- Historically successful mitigation: **chemical flush + integrity verification workflow** (proven in 2019)

**Compliance Framework:**
- Sub-threshold pressure events require **immediate shutdown**
- **Restart prohibited** until: integrity verification log, pressure hold test at 1.3x operating pressure for 4 hours, dual sign-off, compliance log entry
- **Level 3 escalation**: VP Operations and CAIO notified within 30 minutes for HIGH production impact

**Agent Verdict:**
- **Severity:** CRITICAL
- **Confidence:** HIGH (100% evidence coverage: telemetry, risk, maintenance, legacy docs, compliance)
- **Restart Allowed:** **NO** — locked until all validation gates are cleared
- **Mitigation:** Execute the proven 2019 chemical flush workflow; do NOT return to production until integrity verification is complete

---

## UI/UX Design: Industrial Operations Console

The interface is designed as a **compact, high-density operations dashboard** — not a consumer chatbot. It serves three audiences simultaneously:

### 1. Executives
- **Top Summary Strip** — 8 KPI cards showing asset, status, severity, confidence, action, restart gate, and timestamps at a glance
- **Restart Gate Banner** — prominent red/green lock/unlock banner showing the single most important operational decision
- **Decision Panel** — structured recommendation with business risk and compliance implications

### 2. Operations Leaders
- **Anomaly Watchlist** — sidebar cards showing all assets with ANOMALY or CAUTION status
- **Severity & Confidence Badges** — color-coded CRITICAL / WARNING / NORMAL and HIGH / MEDIUM / LOW confidence
- **Restart Conditions** — explicit, bulleted gates that must be cleared before production restart
- **Safety & Compliance Note** — escalation level and notification requirements

### 3. Engineers
- **Evidence Pack (5 Tabs)** — every data source used in the recommendation, with:
  - Full data tables (telemetry, risk metrics)
  - Document snippets with match counts (legacy search)
  - Compliance excerpts with lineages
  - **"Why It Mattered" callouts** — explaining how each evidence piece influenced the diagnosis
- **Tool Trace Tab** — chronological log of every MCP tool call and resource read with timestamps, enabling full forensic audit
- **Alternative Considerations** — ranked hypotheses the agent considered and rejected, with rationale

### Design Language
| Element | Implementation |
|---|---|
| **Palette** | Neutral slate base (`#f1f5f9`), dark text (`#0f172a`), single steel-blue accent (`#2563eb`) |
| **Severity Colors** | Red = critical/stop, Amber = warning/caution, Green = safe/proceed, Blue/gray = informational |
| **Typography** | Compact (0.65–0.88rem), strong hierarchy via weight and uppercase labels |
| **Spacing** | Tight; information density prioritized over whitespace |
| **Badges** | Uppercase, letter-spaced, color-coded pills for status, severity, confidence, restart |
| **Stale Data Chips** | Amber "STALE" chip on telemetry >2 hours old — prevents decisions on outdated data |
| **Empty State** | System overview metrics and instructional guidance before first run |

---

## Key Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Dynamic Discovery** | Agent calls `tools/list` and `resources/list` at runtime; no hardcoded tool names |
| **Evidence Traceability** | Every recommendation cites which tools, resources, and documents informed the decision |
| **Explainability** | "Why It Mattered" callouts on every evidence tab; alternative hypotheses surfaced |
| **Safety Guardrails** | Compliance resource is read *before* recommendation; escalation triggers are explicit; restart gate is binary |
| **Deterministic Fallback** | Pseudo-agent planner ensures the prototype works end-to-end without external LLM APIs |
| **Modular Boundaries** | MCP server abstraction allows swapping SQLite -> real historian, filesystem -> real SharePoint |
| **Bounded Execution** | `MAX_TOOL_CALLS` prevents runaway agent loops |
| **Stale Data Detection** | Telemetry timestamps checked against 2-hour threshold; stale chips warn operators |
| **Confidence Scoring** | Evidence coverage score (0-100) based on telemetry, risk, maintenance, legacy, compliance availability |

---

## How This Maps to Real Enterprise Deployment

| Pilot Component | Production Equivalent |
|-----------------|---------------------|
| SQLite database | OSIsoft PI Historian, AspenTech IP.21, InfluxDB, or SAP HANA |
| Local filesystem (SharePoint sim) | Microsoft Graph API + Azure Cognitive Search / SharePoint Online |
| In-process MCP server | Standalone MCP microservice (FastAPI/Node) with OAuth2, RBAC, rate limiting, audit logging |
| Deterministic planner | OpenAI GPT-4 / Anthropic Claude with function calling + retrieval augmentation |
| Streamlit UI | React/Next.js operational dashboard, embedded SAP/Maximo widget, or Ignition Perspective module |
| Synthetic data | Real SCADA telemetry, CMMS work orders, drilling/completion reports, DCS alarm logs |
| `search_legacy_share` | Azure AI Search, Elasticsearch, Amazon Kendra, or industrial document AI pipelines |

---

## Technology Stack

- **Python 3.11+**
- **Streamlit** — Industrial operations console
- **SQLite** — Modern structured data store (historian simulation)
- **Local filesystem** — Legacy unstructured document repository (SharePoint simulation)
- **JSON-RPC 2.0 style** — MCP protocol boundary (transport-agnostic)
- **ReAct pattern** — Agent reasoning loop (Thought -> Discover -> Act -> Synthesize)

---

## License

MIT License — Built for demonstration and educational purposes.

---

## Contact

**Prakash Krishnan** — Chief AI Officer / Principal AI Architect  
[GitHub: @prakashkrish-DataGeek](https://github.com/prakashkrish-DataGeek)
