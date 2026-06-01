# AI Supply Chain Risk Assistant

## 1. Overview

### Product Name

AI Supply Chain Risk Assistant

### Product Type

Enterprise AI Decision Support Platform

### Vision

Enable supply chain managers to identify, monitor, and understand supply chain risks using real-time external intelligence and AI-powered analysis.

The platform aggregates data from weather services, logistics disruption feeds, and global news sources to provide actionable risk insights through dashboards and conversational AI.

---

# 2. Problem Statement

Supply chain teams rely on fragmented information sources to monitor operational risks.

Important signals are distributed across:

* News websites
* Weather alerts
* Port disruption reports
* Transportation updates
* Supplier communications

Teams spend significant time gathering information before making decisions.

This leads to:

* Slow reaction times
* Increased operational costs
* Delivery delays
* Inventory shortages
* Poor risk visibility

Organizations require a centralized platform capable of continuously monitoring risk indicators and providing actionable summaries.

---

# 3. Goals

### Business Goals

* Improve visibility into global supply chain disruptions
* Reduce time spent collecting information
* Enable faster risk assessment

### Technical Goals

* Demonstrate agentic AI architecture
* Implement retrieval-augmented generation (RAG)
* Integrate multiple external data sources
* Provide explainable risk scoring
* Build a Dockerized React + FastAPI application

---

# 4. Target Users

## Primary User

Supply Chain Manager

Responsibilities:

* Monitor disruptions
* Evaluate transportation risks
* Track regional issues
* Communicate risks to stakeholders

---

## Secondary User

Operations Analyst

Responsibilities:

* Investigate incidents
* Review historical disruptions
* Generate reports

---

# 5. User Stories

## Dashboard

As a supply chain manager,

I want to view current global risk indicators,

So that I can quickly understand emerging threats.

---

## Risk Investigation

As an analyst,

I want to explore disruption events by region,

So that I can understand root causes.

---

## Conversational Search

As a manager,

I want to ask natural language questions,

So that I can receive summarized intelligence without manual research.

---

## Risk Monitoring

As a manager,

I want risk scores to update automatically,

So that I can react to changing conditions.

---

# 6. MVP Scope

## Included

### Data Collection

Weather alerts

News articles

Trade volume data

Historical shipment and delivery data

---

### Risk Engine

Region-based risk scores

Risk classification:

* Low
* Medium
* High

---

### AI Assistant

Natural language interface

Example:

"What risks affect Europe today?"

"What logistics disruptions occurred this week?"

"Summarize shipping risks in Germany."

---

### RAG System

Document ingestion

Vector search

Source citations

---

### Dashboard

Risk overview

Regional breakdown

Disruption feed

Chat assistant

---

## Excluded (Future Versions)

Direct supplier system integration

ERP integration

Predictive forecasting

User management

Alert subscriptions

Mobile application

---

# 7. Functional Requirements

## FR-1 Data Ingestion

System shall ingest external data every hour.

Recommended MVP sources:

* OpenWeather API
* NewsAPI
* UN Comtrade API
* Kaggle supply chain dataset, such as Supply Chain Dataset or DataCo Supply Chain Dataset

Source responsibilities:

* OpenWeather API provides live weather risk signals.
* NewsAPI provides live supply chain disruption articles for RAG.
* UN Comtrade API provides import, export, and country trade activity for dashboard analytics.
* Kaggle historical data provides shipment, delivery, delay, and warehouse records for trends and risk score calibration.

NewsAPI search keywords:

* supply chain disruption
* shipping delays
* port congestion
* logistics crisis
* container shortage
* factory shutdown

Example weather event:

```json
{
  "region": "Germany",
  "event": "Heavy Storm",
  "severity": "High",
  "timestamp": "2026-06-02"
}
```

Example news document:

```json
{
  "title": "Port congestion affects shipping routes",
  "content": "Latest disruption details...",
  "region": "Europe",
  "source": "Reuters"
}
```

Optional future source:

* Port Data API or CSV disruption data

---

## FR-2 Document Processing

System shall:

* Clean text
* Generate embeddings
* Store vectors in Qdrant

---

## FR-3 Risk Scoring

System shall calculate regional risk scores.

Inputs:

* Weather severity
* Disruption frequency
* Negative sentiment
* Historical delivery delay patterns
* Trade activity changes

Output:

0–100 risk score

---

## FR-4 AI Assistant

System shall answer natural language questions using:

* Retrieved documents
* Risk database
* Current risk scores

Responses must include sources.

---

## FR-5 Risk Dashboard

Dashboard shall display:

Global Risk Index

High-Risk Regions

Recent Disruptions

Risk Trends

---

## FR-6 Disruption Feed

Users shall view chronological disruption events.

Each event contains:

* Title
* Region
* Source
* Severity
* Timestamp

---

# 8. Non-Functional Requirements

## Performance

Dashboard loads under 3 seconds.

Chat responses under 8 seconds.

---

## Reliability

99% ingestion success rate.

Graceful handling of API failures.

---

## Scalability

Support:

100,000+ documents

10,000+ vectors

Concurrent users

---

## Security

Environment variables secured through local `.env` files for development and deployment platform secrets in production.

No sensitive business data stored.

---

# 9. Technical Architecture

## Frontend

React

TypeScript

TailwindCSS

shadcn/ui or equivalent component system

Recharts

Leaflet or React Map GL

---

## Backend

FastAPI

LangGraph

OpenAI

Python service modules

---

## Database

Supabase datastore

Stores:

* Risk scores
* Events
* Metadata

---

## Vector Database

Qdrant Cloud

Stores:

* News embeddings
* Weather summaries
* Disruption reports

---

## Scheduled Jobs

Dockerized ingestion service

Tasks:

* Fetch news
* Fetch weather
* Fetch port or CSV disruption data
* Generate risk scores

Frequency:

Every hour

---

# 10. AI Architecture

## Agent

Supply Chain Risk Agent

### Tools

News Retrieval Tool

Weather Tool

Port Disruption Tool

Risk Score Lookup Tool

Qdrant Search Tool

---

### Workflow

User Question

↓

Agent

↓

Determine Required Tools

↓

Retrieve Context

↓

Generate Response

↓

Return Sources

---

# 11. Database Schema

## regions

id

name

risk_score

last_updated

---

## disruptions

id

title

description

region

severity

source

created_at

---

## documents

id

title

source

url

published_at

embedding_id

---

## trade_metrics

id

country

partner_country

trade_flow

commodity

period

trade_value

quantity

created_at

---

## historical_shipments

id

order_id

region

warehouse

delivery_status

delay_days

shipping_mode

created_at

---

# 12. Dashboard Pages

## Page 1

Executive Dashboard

Components:

* Global Risk Index
* Risk Trend Chart
* High Risk Regions
* Recent Events

---

## Page 2

Regional Risk Explorer

Components:

* Interactive map
* Risk breakdown
* Regional trends

---

## Page 3

AI Assistant

Components:

* Chat interface
* Source citations
* Suggested questions

---

## Page 4

Disruption Feed

Components:

* Timeline
* Filters
* Severity indicators

---

# 13. Success Metrics

## Product Metrics

Average response time

Daily active users

Questions per session

---

## Technical Metrics

Ingestion success rate

Embedding generation success rate

Retrieval relevance

API uptime

---

# 14. Deployment

Hosting: Dockerized deployment target

Frontend: React

Backend: FastAPI

Database: Supabase datastore

Vector Database: Qdrant Cloud

AI Model: OpenAI GPT-5

Containers: Docker

CI/CD: GitHub
