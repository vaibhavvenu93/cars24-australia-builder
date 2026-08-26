# CARS24 Australia — Intelligence OS

> An outside-in operating prototype built for the CARS24 Australia Business Builder application.

**Live prototype:**  
https://cars24-australia-os.streamlit.app

---

## I wasn't trying to build another dashboard.

I wanted to answer a different question:

> **If I joined CARS24 Australia tomorrow, how would I figure out what actually deserves attention — and turn that into action?**

A business like CARS24 already generates enormous amounts of information across CRM, inventory, acquisition, refurbishment, finance, logistics, marketing and customer operations.

The harder problem is connecting those signals.

A slow-moving vehicle is not just an inventory problem.

It might be:

- an acquisition problem,
- a pricing problem,
- a location problem,
- a refurbishment delay,
- weak local demand,
- poor lead conversion,
- or simply capital sitting in the wrong place.

So I built a prototype intelligence layer that tries to connect those dots.

The result is the **CARS24 Australia Intelligence OS**.

```text
DATA
 ↓
ECONOMICS
 ↓
SIGNALS
 ↓
OPPORTUNITIES
 ↓
SCENARIOS
 ↓
EXPERIMENTS
 ↓
DECISIONS
 ↓
EXECUTIVE ACTION
```

---

# Why I built this

The Business Builder role struck me as unusual because it sits somewhere between:

**strategy × operations × product × analytics × execution**

Rather than only writing why my background might fit that combination, I decided to treat the application as a miniature version of the job.

I started by researching the Australian used-car operating model and asking:

> If I had to improve this business, what would I need to understand before changing anything?

That led to five questions:

1. Where is the business actually making or losing money?
2. Where is inventory or capital getting stuck?
3. Which operational constraints matter economically?
4. Which interventions should we test first?
5. What should leadership pay attention to today?

The prototype grew around those questions.

---

# The operating thesis

A used-car business is ultimately a capital allocation and operating velocity system.

Every vehicle moves through a lifecycle:

```text
Acquire
   ↓
Inspect
   ↓
Refurbish
   ↓
Price
   ↓
Locate
   ↓
Market
   ↓
Convert
   ↓
Sell
   ↓
Warranty / Return
```

Every additional day has an economic consequence.

Every incorrect acquisition decision has an economic consequence.

Every refurbishment bottleneck has an economic consequence.

Every mismatch between inventory and regional demand has an economic consequence.

And every improvement in conversion, inventory velocity or operational throughput potentially releases capital.

So the OS treats the **vehicle as the core economic unit** and tries to connect decisions around it.

---

# What the prototype does

The application is organised into four operating environments.

## 1. Executive Intelligence

A leadership layer answering:

> **What needs leadership attention today?**

It aggregates signals from the other intelligence engines into a single operating view.

### Command Centre

Surfaces:

- revenue
- sales
- capital at risk
- open decisions
- modeled opportunity
- highest-value operating signals
- recommended interventions

Instead of asking leadership to inspect multiple dashboards, the system attempts to rank what matters by **economic impact and confidence**.

### Morning Brief

Generates a concise operating brief across:

- Growth
- Inventory
- Operations
- Builder activity

The intention is simple:

> Leadership should start with decisions, not dashboards.

---

# 2. Growth Intelligence

Growth is treated as an operating system rather than simply a marketing funnel.

The engine looks across:

```text
Lead
 ↓
Response
 ↓
Qualification
 ↓
Test Drive
 ↓
Offer
 ↓
Sale
```

It can identify patterns such as:

- weak enquiry → test-drive conversion,
- slow response times,
- location-level conversion gaps,
- model-level demand differences,
- funnel leakage.

The important part is not detecting the metric.

It is translating the metric into an intervention.

For example:

```text
Melbourne SUV demand
        ↓
Conversion below benchmark
        ↓
Response-time constraint detected
        ↓
Economic opportunity estimated
        ↓
Intervention recommended
        ↓
Experiment created
```

---

# 3. Inventory Intelligence

Inventory is capital.

The prototype therefore evaluates vehicles through both operating and economic lenses.

It looks at:

- acquisition cost
- refurbishment cost
- holding cost
- inventory age
- expected contribution
- regional demand
- location
- lifecycle risk
- potential transfer economics

This allows the system to surface questions such as:

> Should this vehicle still be here?

> Should we reprice it?

> Should we move it?

> Should we stop buying similar inventory?

> Is the expected contribution still attractive after holding and refurbishment costs?

---

# 4. Operations Intelligence

Operations Intelligence looks for constraints in the physical operating system.

### Location Performance

Compares locations across:

- sales
- contribution
- conversion
- refurbishment speed
- inventory age
- operating score

The goal is not simply ranking locations.

It is identifying **why** one location performs differently from another.

### Vendor Intelligence

Invoice price alone does not determine vendor economics.

The prototype therefore evaluates refurbishment vendors across:

- cost
- turnaround time
- SLA breaches
- rework
- downstream operating impact

This creates a **true vendor performance score**.

### Transfer Intelligence

A vehicle may be healthy inventory but sitting in the wrong market.

The transfer engine compares:

- current demand
- destination demand
- transport cost
- expected days saved
- modeled contribution upside
- confidence

and generates inventory-transfer recommendations.

### Action Centre

Signals from across Operations Intelligence are converted into one ranked operating queue.

Examples include:

- location intervention
- inventory transfer
- recon bottleneck
- vendor review

Actions are prioritised using expected economic impact, severity and confidence.

---

# 5. Builder

Finding problems is only half the job.

The Builder environment asks:

> **Where should we build next?**

It contains four components.

### Opportunity Radar

Combines signals from Growth, Inventory and Operations into a ranked portfolio of opportunities.

Each opportunity includes:

- domain
- priority
- evidence
- recommended action
- modeled economic impact
- confidence

### Scenario Lab

Before committing capital or execution capacity, assumptions can be changed.

Example:

```text
Response time improvement: 25%
Test-drive conversion lift: +5pp
Additional inventory: +10%
```

The system then estimates:

```text
Baseline economics
        ↓
Modeled economics
        ↓
Economic delta
        ↓
Expected improvement
```

The purpose isn't prediction.

It is structured decision-making.

### Experiments

Opportunities can become measurable operating experiments.

Each experiment includes:

- hypothesis
- owner
- baseline
- target
- duration
- expected impact
- confidence
- status

This creates a loop:

```text
Signal
 ↓
Hypothesis
 ↓
Experiment
 ↓
Evidence
 ↓
Scale / Stop / Iterate
```

### Data Hub

The prototype includes a lightweight ingestion layer.

Operational CSV/XLS/XLSX datasets can be uploaded.

The system attempts to:

1. detect the operational domain,
2. normalise column names,
3. map fields into a canonical schema,
4. determine which intelligence capabilities could become available.

Supported conceptual domains include:

- CRM
- Inventory
- Finance
- Reconditioning
- Logistics
- Marketing
- Customer
- Market Data

---

# Integrations

I deliberately designed the prototype as an **intelligence layer above existing systems**, rather than imagining CARS24 replacing its operational stack.

Conceptually:

```text
CRM
Inventory / Fleet
Finance
Reconditioning
Logistics
Marketing
Customer Systems
Market Data
        │
        ▼
┌──────────────────────────────┐
│      Canonical Data Layer    │
└──────────────────────────────┘
        │
        ▼
┌──────────────────────────────┐
│      Intelligence Engines    │
│                              │
│ Growth                       │
│ Inventory                    │
│ Operations                   │
│ Opportunity                  │
│ Scenario                     │
│ Executive                    │
└──────────────────────────────┘
        │
        ▼
Decision / Experiment / Action
```

The prototype currently uses simulated connections.

With actual system access, adapters would sit between source systems and the canonical data layer.

---

# The architecture

The repository separates business logic from the interface.

```text
cars24-australia-builder/
│
├── app/
│   ├── intelligence_os.py
│   └── views/
│       ├── executive.py
│       ├── operations.py
│       └── builder.py
│
├── engines/
│   ├── executive_intelligence.py
│   ├── operations_intelligence.py
│   ├── builder_intelligence.py
│   ├── opportunity_engine.py
│   ├── location_engine.py
│   ├── scenario_engine.py
│   ├── unit_economics.py
│   └── data_hub.py
│
├── data/
│   └── synthetic_vehicle_portfolio.json
│
└── tests/
```

The Streamlit interface is intentionally thin.

Most decision logic lives inside the intelligence engines.

That separation matters because the eventual interface could be:

- Streamlit
- an internal web application
- Slack
- Teams
- email
- an API
- an AI agent

without rebuilding the underlying decision logic.

---

# Example: one decision journey

Imagine a vehicle has been sitting in Adelaide longer than expected.

A traditional dashboard might show:

```text
Inventory age: 54 days
```

The OS should instead ask:

```text
Why?
```

and then reason across systems:

```text
Vehicle ageing
      ↓
Local demand weak
      ↓
Brisbane demand stronger
      ↓
Expected holding cost increasing
      ↓
Transfer cost = $535
      ↓
Expected inventory days saved = 5
      ↓
Expected margin improvement positive
      ↓
TRANSFER RECOMMENDATION
```

That recommendation then appears in:

**Transfer Intelligence → Action Centre → Executive Intelligence**

The idea is to connect information to a decision path.

---

# What is real and what is simulated

This distinction matters.

### Real

The prototype contains functioning:

- economic models
- opportunity rules
- transfer logic
- location scoring
- vendor scoring
- scenario simulation
- dataset detection
- schema mapping
- capability registry
- experiment framework
- executive aggregation
- Streamlit application
- automated tests

### Simulated

The prototype does **not** connect to CARS24 production systems.

All vehicle, customer, vendor, location and financial information is synthetic.

Integration states shown in the application represent what connected infrastructure could look like.

No confidential or proprietary CARS24 information was used.

---

# Testing

The repository currently contains **35 automated tests** covering areas including:

- dataset detection
- schema normalisation
- system registry
- location intelligence
- transfer recommendations
- opportunity detection
- scenario simulation
- unit economics

Run:

```bash
python3 -m pytest -v
```

Expected:

```text
35 passed
```

---

# Running locally

Clone the repository:

```bash
git clone https://github.com/vaibhavvenu93/cars24-australia-builder.git
cd cars24-australia-builder
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
python3 -m pytest -v
```

Launch the application:

```bash
python3 -m streamlit run app/intelligence_os.py
```

Then open:

```text
http://localhost:8501
```

---

# What I would do with real CARS24 access

This prototype starts with hypotheses.

Inside the business, I would start with evidence.

### Phase 1 — Understand

Map:

- vehicle lifecycle
- system architecture
- unit economics
- decision ownership
- location economics
- acquisition process
- refurbishment workflow
- pricing
- customer funnel
- existing dashboards and metrics

### Phase 2 — Find constraints

Identify where the largest pools of:

```text
Lost contribution
+
Trapped capital
+
Operational friction
+
Customer friction
```

exist.

### Phase 3 — Prioritise

Rank opportunities using something like:

```text
Economic impact
×
Confidence
×
Speed to learn
÷
Execution complexity
```

### Phase 4 — Experiment

Run small interventions with:

- clear hypotheses
- owners
- baselines
- targets
- time windows
- measurable economics

### Phase 5 — Scale

Only after evidence exists:

```text
Automate
Standardise
Productise
Scale
```

---

# What I would not do

I would not assume this prototype represents how CARS24 actually operates internally.

It doesn't.

That would require access to the people, systems, economics and operating context inside the business.

I also would not begin by proposing a large technology transformation.

The first objective would be much simpler:

> **Find one economically meaningful constraint, understand it deeply, fix it, measure the result and repeat.**

The OS is simply a demonstration of how I think that loop could eventually become systematic.

---

# Why this exists

This repository is ultimately not an attempt to show that I can build a Streamlit application.

AI makes building software increasingly cheap.

The scarce part is deciding:

**what deserves to be built, why it matters economically, what evidence supports it, and whether it actually changes an outcome.**

That's the part of the Business Builder role that interests me.

I like moving between:

```text
messy problem
     ↓
data
     ↓
economics
     ↓
hypothesis
     ↓
product / process
     ↓
execution
     ↓
measured outcome
```

So rather than send another application explaining that I like operating in ambiguity, I decided to spend some time operating in it.

This repository is the result.

---

## Disclaimer

This is an independent application prototype.

It is not affiliated with, endorsed by, commissioned by, or built using confidential information from CARS24.

All operational datasets, financial values, customer information, vendor information and vehicle records used in the prototype are synthetic or illustrative.
