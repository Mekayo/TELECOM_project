# AI-Powered Network Diagnostics & Optimization Agent — Implementation Plan

An AI agent that continuously monitors telecom infrastructure telemetry data, detects congestion, predicts hardware failures, and autonomously recommends re-routing/provisioning strategies with contextual explanations for engineers.

## Current State

| Asset | Details |
|-------|---------|
| [main.py](file:///d:/TELECOM_project/main.py) | Collects real-time telemetry (cpu, memory, latency, bandwidth, packet_loss, crc_errors) via `psutil` |
| [EDA_Telemetry_Analysis.ipynb](file:///d:/TELECOM_project/EDA_Telemetry_Analysis.ipynb) | Exploratory data analysis notebook |
| CSV datasets (~83 KB each) | In `data/Formed_data/` and `data/transformed_data/` |

## User Review Required

> [!IMPORTANT]
> **Scope decision**: This plan covers a full production-grade agent. Please confirm if you'd like to:
> 1. **Full build** — All 5 phases (estimated ~40+ files, significant effort)
> 2. **MVP first** — Phase 1 + 2 + minimal Phase 4 (core intelligence + simple dashboard)
> 3. **Backend only** — Phase 1 + 2 + 3 (no web UI)

> [!WARNING]
> **LLM integration**: Phase 3 includes an "explanation generator." This can be:
> - **Rule-based** (zero cost, deterministic, no API key needed)
> - **LLM-powered** (requires an API key for OpenAI/Gemini/etc., richer explanations)
> - Please confirm your preference.

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Dashboard                        │
│  (Real-time topology, alerts, recommendations panel)    │
├─────────────────────────────────────────────────────────┤
│               FastAPI + WebSocket Server                │
├──────────┬──────────┬──────────┬────────────────────────┤
│ Congestion│ Failure  │ Re-route │ Explanation            │
│ Detector  │ Predictor│ Engine   │ Generator              │
├──────────┴──────────┴──────────┴────────────────────────┤
│          Data Pipeline & Feature Engineering            │
├─────────────────────────────────────────────────────────┤
│     Telemetry Collector (psutil + simulated devices)    │
└─────────────────────────────────────────────────────────┘
```

---

## Proposed File Structure

```
d:\TELECOM_project\
├── config.py                      # Centralized configuration
├── main.py                        # Entry point (refactored)
├── requirements.txt               # Dependencies
│
├── data/
│   ├── Formed_data/               # (existing)
│   └── transformed_data/          # (existing)
│
├── src/
│   ├── __init__.py
│   ├── collector/
│   │   ├── __init__.py
│   │   └── telemetry_collector.py # [MODIFIED from main.py] Multi-device collector
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── ingestion.py           # [NEW] Data validation & ingestion
│   │   └── feature_engineering.py # [NEW] Rolling stats, derived features
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── congestion_detector.py # [NEW] Anomaly detection (Isolation Forest / Z-score)
│   │   ├── failure_predictor.py   # [NEW] Time-series forecasting (XGBoost / LSTM)
│   │   └── alert_manager.py       # [NEW] Threshold engine + alert state machine
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── optimizer.py           # [NEW] Re-routing & provisioning recommendations
│   │   ├── explainer.py           # [NEW] Contextual explanation generator
│   │   └── action_log.py          # [NEW] Audit trail for all agent actions
│   │
│   └── api/
│       ├── __init__.py
│       ├── server.py              # [NEW] FastAPI app with REST endpoints
│       ├── websocket.py           # [NEW] Real-time telemetry streaming
│       └── routes.py              # [NEW] API route definitions
│
├── dashboard/
│   ├── index.html                 # [NEW] Main dashboard page
│   ├── index.css                  # [NEW] Styles
│   └── app.js                     # [NEW] Dashboard logic (vanilla JS)
│
├── tests/
│   ├── __init__.py
│   ├── test_collector.py          # [NEW]
│   ├── test_pipeline.py           # [NEW]
│   ├── test_models.py             # [NEW]
│   ├── test_agent.py              # [NEW]
│   └── test_api.py                # [NEW]
│
└── trained_models/                # [NEW] Serialized model artifacts
    └── .gitkeep
```

---

## Phase 1 — Data & Infrastructure Foundation

### [MODIFY] [config.py](file:///d:/TELECOM_project/config.py)
- Centralized settings: device list, thresholds, DB path, model paths, API port
- Environment variable overrides via `os.getenv()`

### [NEW] [telemetry_collector.py](file:///d:/TELECOM_project/src/collector/telemetry_collector.py)
- Refactor `main.py` into a class-based collector  
- Support **multiple simulated devices** (Router 1–5, Switch 1–3) with device-specific noise profiles
- Add fault injection modes (spike CPU, saturate bandwidth) for training data generation
- Write telemetry to SQLite + CSV simultaneously

### [NEW] [ingestion.py](file:///d:/TELECOM_project/src/pipeline/ingestion.py)
- Schema validation (pydantic models for telemetry records)
- NULL/outlier handling, type coercion
- Batch and stream ingestion modes

### [NEW] [feature_engineering.py](file:///d:/TELECOM_project/src/pipeline/feature_engineering.py)
- Rolling statistics: 5min/15min/1hr windows for all metrics
- Derived features: `bandwidth_utilization_ratio`, `latency_jitter`, `error_rate_trend`
- Device-level and network-wide aggregations

---

## Phase 2 — AI/ML Core Engine

### [NEW] [congestion_detector.py](file:///d:/TELECOM_project/src/models/congestion_detector.py)
- **Isolation Forest** for multivariate anomaly detection on `(latency, packet_loss, bandwidth_utilization)`
- **Z-score alerting** for single-metric spikes
- Outputs: congestion score (0–1), affected metrics, severity level
- Train on existing CSV data, retrain on schedule

### [NEW] [failure_predictor.py](file:///d:/TELECOM_project/src/models/failure_predictor.py)
- **XGBoost classifier** for failure probability within next N hours
- Features: rolling CRC error trends, CPU/memory trends, historical failure correlation
- Outputs: failure probability, predicted failure type, confidence interval
- Model serialization with `joblib`

### [NEW] [alert_manager.py](file:///d:/TELECOM_project/src/models/alert_manager.py)
- Configurable threshold rules (from `config.py`)
- Alert state machine: `NORMAL → WARNING → CRITICAL → RECOVERING → NORMAL`
- Alert deduplication and cooldown windows
- Unified alert format combining model outputs and threshold breaches

---

## Phase 3 — Autonomous Optimization Agent

### [NEW] [optimizer.py](file:///d:/TELECOM_project/src/agent/optimizer.py)
- **Re-routing engine**: Given congested links, suggest alternate paths using a weighted graph model of the network topology
- **Provisioning advisor**: Recommend scaling up bandwidth, adding redundant links, or replacing aging hardware based on failure predictions
- Priority scoring and conflict resolution between recommendations

### [NEW] [explainer.py](file:///d:/TELECOM_project/src/agent/explainer.py)
- Generate human-readable explanations for every recommendation
- Template-based approach with dynamic data insertion:
  > *"Router 3 shows a 78% probability of CPU failure within 12 hours based on a sustained upward trend in CPU utilization (avg 89% over last 3 hours) combined with increasing CRC errors (+340% vs. baseline). Recommended action: migrate traffic to Router 4 and schedule preventive maintenance."*
- Severity-appropriate language and actionable next steps

### [NEW] [action_log.py](file:///d:/TELECOM_project/src/agent/action_log.py)
- Log every agent decision with timestamp, input data snapshot, recommendation, and explanation
- SQLite-backed audit trail
- Query API for historical analysis

---

## Phase 4 — Dashboard & API

### [NEW] [server.py](file:///d:/TELECOM_project/src/api/server.py)
FastAPI application with endpoints:
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/devices` | List all monitored devices |
| GET | `/api/telemetry/{device_id}` | Latest telemetry for a device |
| GET | `/api/alerts` | Active alerts with filtering |
| GET | `/api/recommendations` | Current optimization recommendations |
| GET | `/api/history` | Historical telemetry & actions |
| WS | `/ws/telemetry` | Real-time telemetry stream |

### [NEW] [dashboard/](file:///d:/TELECOM_project/dashboard/)
- **Network topology view**: Interactive SVG/Canvas showing devices, links, and status
- **Real-time metrics panel**: Live-updating charts (Chart.js) for each device
- **Alert feed**: Chronological alert stream with severity badges
- **Recommendation panel**: Agent suggestions with expandable explanations
- Dark mode, glassmorphism styling, smooth animations

---

## Phase 5 — Verification Plan

### Automated Tests

**Unit tests** — run with:
```bash
python -m pytest tests/ -v --tb=short
```

| Test file | Covers |
|-----------|--------|
| `test_collector.py` | Telemetry record generation, multi-device support |
| `test_pipeline.py` | Schema validation, feature engineering calculations |
| `test_models.py` | Congestion detection accuracy, failure prediction, alert state transitions |
| `test_agent.py` | Re-routing logic, explanation generation, action logging |
| `test_api.py` | API endpoint responses, WebSocket connections |

**Integration test** — end-to-end pipeline:
```bash
python -m pytest tests/ -v -k "integration" --tb=short
```

### Manual Verification
1. **Start the collector**: Run `python -m src.collector.telemetry_collector` and verify telemetry records appear in the database
2. **Trigger an anomaly**: Use the fault-injection mode to spike CPU to 95%+ and verify the congestion detector fires an alert
3. **Check the dashboard**: Open `http://localhost:8000` in a browser, verify live charts update, alerts appear, and recommendations show contextual explanations
4. **Review explanations**: Confirm the explanation text is clear, actionable, and includes specific metric values

---

## Dependencies (`requirements.txt`)

```
psutil>=5.9
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
xgboost>=2.0
joblib>=1.3
pydantic>=2.0
fastapi>=0.100
uvicorn>=0.23
websockets>=12.0
```
