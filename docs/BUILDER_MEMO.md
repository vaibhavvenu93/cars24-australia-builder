# CARS24 Australia — Builder Memo

## Why I built this

I came across the Business Builder opportunity and the part that caught my attention wasn't the title.

It was the mandate.

This looks like a role for someone who can move between strategy, product, operations, growth and execution — understand a messy problem, figure out what matters, and then actually build around it.

That's largely how I've operated throughout my career.

So instead of sending another application explaining that, I wanted to show you how I think.

I spent time looking at CARS24 Australia from the outside and asked myself:

> If I joined tomorrow, where would I start?

I don't have your internal data, economics or operating context, so pretending I know the answer would be silly.

Instead, I built the system I would want in order to find it.

That became the **CARS24 Australia Intelligence OS**.

---

# My outside-in hypothesis

A business like CARS24 is an unusually interesting operating system.

A vehicle moves through:

Acquire → Inspect → Recondition → Price → Locate → Market → Convert → Sell

But every stage interacts with several others.

A conversion problem might actually be an inventory problem.

An inventory problem might actually be a pricing problem.

A margin problem might originate in acquisition.

A slow-moving vehicle might be perfectly good inventory sitting in the wrong geography.

A cheap refurbishment vendor might become expensive once turnaround time and rework are considered.

And every day inventory sits somewhere has a capital consequence.

My hypothesis therefore isn't:

> CARS24 needs another dashboard.

It's:

> There may be significant value in connecting operating signals to their economic consequences and making the resulting decisions easier and faster.

That's what the prototype explores.

---

# What I built

I built an outside-in prototype of an operating intelligence layer across five environments.

### Executive

A Command Centre and Morning Brief answering:

> What deserves leadership attention today?

Instead of showing every metric, it ranks operating signals using modeled economic impact and confidence.

### Growth

Looks for funnel leakage across location, vehicle segment and customer journey.

For example, the synthetic environment detects a Melbourne SUV cohort where enquiry → test-drive conversion materially trails the network benchmark.

Rather than stopping at the metric, the system estimates the opportunity and suggests what to investigate next.

### Inventory

Treats each vehicle as a capital-allocation decision.

The system looks at ageing, holding cost, expected contribution, regional demand and inventory positioning.

### Operations

Explores location performance, vendor economics, refurbishment performance and vehicle-transfer opportunities.

### Builder

Takes detected problems and turns them into:

Opportunity → Scenario → Experiment → Action

The objective is to create a closed operating loop rather than another reporting layer.

---

# What I deliberately did not do

I did not try to reverse-engineer CARS24's actual internal performance.

The data in this prototype is synthetic.

The assumptions are hypotheses.

And the recommendations are demonstrations of how the decision system could work — not claims about what CARS24 should actually do.

The real work would begin after joining.

---

# What I would do first

## Days 1–30 — Find the constraint

I would spend the first month understanding the operating system.

Not just dashboards.

I would sit with people across:

- acquisition
- pricing
- inventory
- sales
- growth
- refurbishment
- logistics
- finance
- customer operations

and map:

**how vehicles move**

**how customers move**

**how money moves**

**how decisions get made**

Then connect those workflows to actual economics.

The objective would be to identify a small number of constraints where improvement could materially affect:

- contribution
- conversion
- inventory velocity
- working capital
- customer experience

I'd rather find one $1M problem than create twenty dashboards.

---

# Days 31–60 — Prove something

Once the highest-value constraint is identified, I would build around it.

That might mean:

- changing a process,
- building an internal tool,
- changing pricing logic,
- redesigning a funnel,
- automating a workflow,
- changing inventory allocation,
- improving a vendor system,
- or running a completely different operating experiment.

The form of the solution matters less than the outcome.

Every intervention should have:

**Baseline → Hypothesis → Owner → Experiment → Metric → Economic outcome**

By Day 60, I would want at least one intervention producing measurable evidence.

---

# Days 61–90 — Build the machine

Only after something works would I systematise it.

That means:

- automate repeatable decisions,
- standardise successful workflows,
- build tooling where tooling is justified,
- establish operating metrics,
- create ownership,
- and replicate successful interventions across locations or cohorts.

The Intelligence OS I built is one possible representation of what that operating layer could eventually become.

But I would let the business determine what actually deserves to be built.

---

# How I think about the role

I don't see Business Builder as a strategy role.

And I don't see it purely as a product role.

I see it as:

> **Find important problems. Understand them economically. Build solutions. Own the outcome.**

Sometimes the answer will be software.

Sometimes it will be sales.

Sometimes operations.

Sometimes analytics.

Sometimes process.

Sometimes simply getting five people into a room and changing how a decision gets made.

That's the kind of ambiguity I enjoy.

---

# Why me

I've spent much of my career moving between functions rather than staying inside one.

I've launched markets, built GTM engines, run operations, worked alongside founders, built products and automations, sold enterprise solutions, managed teams and worked on businesses from zero to scale.

More recently I've increasingly been building with AI myself — not just using AI tools, but turning operating problems into working products, workflows and decision systems.

That combination is why this particular role caught my attention.

I don't want to advise from the sidelines.

I like being close enough to the problem that I'm accountable for whether the solution actually works.

---

# The question I'd like to answer

I don't know whether the hypotheses in this prototype are right.

That's precisely why I'd like to talk.

Give me the real operating context, the people who understand it and the data behind it, and I'd like to find the problems actually worth solving.

Then build around them.

---

**Live prototype:**  
https://cars24-australia-os.streamlit.app

**Repository:**  
CARS24 Australia Intelligence OS

**Architecture:**  
`docs/architecture/README.md`

---

*Independent application prototype. All operating and financial data used in the demonstration is synthetic. No confidential CARS24 information was used.*
