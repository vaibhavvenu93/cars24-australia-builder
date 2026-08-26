# CARS24 Australia Intelligence OS — Architecture

## System Model

```mermaid
flowchart TB

subgraph SOURCES["1 · OPERATIONAL SYSTEMS"]
CRM[CRM / Leads]
INV[Vehicle Inventory]
SALE[Sales]
PRICE[Pricing]
RECON[Reconditioning]
MKT[Marketing]
FIN[Finance]
end

subgraph DATA["2 · DATA FOUNDATION"]
INGEST[Ingestion]
WAREHOUSE[(Operational Warehouse)]
SEMANTIC[Canonical Metrics Layer]
end

subgraph INTELLIGENCE["3 · INTELLIGENCE ENGINES"]
GROWTH[Growth Intelligence]
INVENTORY[Inventory Intelligence]
OPS[Operations Intelligence]
MARKET[Market Intelligence]
end

subgraph SIGNAL["4 · SIGNAL ENGINE"]
ANOMALY[Anomaly Detection]
BENCH[Benchmarking]
FORECAST[Forecasting]
IMPACT[Economic Impact]
end

subgraph DECISION["5 · DECISION ENGINE"]
PRIORITY[Prioritisation]
CAUSE[Root Cause]
RECOMMEND[Recommendations]
CONFIDENCE[Confidence]
end

subgraph EXPERIENCE["6 · OPERATING EXPERIENCES"]
EXEC[Executive Command Centre]
BRIEF[Morning Brief]
INVESTIGATE[Investigation Workspace]
SCENARIO[Scenario Engine]
EXPERIMENT[Experiment Builder]
end

subgraph LOOP["7 · LEARNING LOOP"]
ACTION[Human Decision]
OUTCOME[Outcome Measurement]
LEARN[Learn / Recalibrate]
end

CRM --> INGEST
INV --> INGEST
SALE --> INGEST
PRICE --> INGEST
RECON --> INGEST
MKT --> INGEST
FIN --> INGEST

INGEST --> WAREHOUSE
WAREHOUSE --> SEMANTIC

SEMANTIC --> GROWTH
SEMANTIC --> INVENTORY
SEMANTIC --> OPS
SEMANTIC --> MARKET

GROWTH --> ANOMALY
INVENTORY --> ANOMALY
OPS --> ANOMALY
MARKET --> ANOMALY

ANOMALY --> BENCH
BENCH --> FORECAST
FORECAST --> IMPACT

IMPACT --> PRIORITY
PRIORITY --> CAUSE
CAUSE --> RECOMMEND
RECOMMEND --> CONFIDENCE

CONFIDENCE --> EXEC
CONFIDENCE --> BRIEF
CONFIDENCE --> INVESTIGATE

INVESTIGATE --> SCENARIO
INVESTIGATE --> EXPERIMENT

EXEC --> ACTION
BRIEF --> ACTION
SCENARIO --> ACTION
EXPERIMENT --> ACTION

ACTION --> OUTCOME
OUTCOME --> LEARN
LEARN --> SEMANTIC
```

---

## Core Principle

The architecture deliberately separates:

**Data → Intelligence → Signals → Decisions → Actions → Outcomes**

This allows individual components to evolve independently.

The Streamlit application is therefore an interface to the intelligence system rather than the intelligence system itself.

## Production Evolution

The prototype currently uses synthetic datasets and local intelligence logic.

A production implementation could progressively replace these components with:

- warehouse-native datasets
- streaming operational events
- governed semantic metrics
- statistical anomaly detection
- forecasting models
- causal / experiment measurement
- LLM-assisted investigation
- agentic workflows
- human approval gates
- outcome-based learning

The architectural objective is a closed-loop decision system rather than a traditional BI stack.
