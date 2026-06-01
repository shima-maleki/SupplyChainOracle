# AGENT.md

# 1. Project Mission

Build the AI Supply Chain Risk Assistant described in `docs/PRD.md` and `docs/architecture.md`.

The product is an enterprise AI decision support platform for supply chain managers and operations analysts. It should collect risk signals from external sources, calculate regional risk scores, and provide a dashboard plus an AI assistant with source citations.

Keep the project understandable for a Junior AI Engineer. Prefer clear, simple, explainable implementations before advanced abstractions.

---

# 2. Source of Truth

Before implementing features, read these files:

1. `docs/PRD.md`
2. `docs/architecture.md`
3. `AGENT.md`

If requirements conflict, follow this order:

1. User's latest instruction
2. `docs/PRD.md`
3. `docs/architecture.md`
4. `AGENT.md`

---

# 3. Target Architecture

Use this stack:

Frontend:

* Next.js 15
* TypeScript
* TailwindCSS
* shadcn/ui
* Recharts
* Map visualization

Backend:

* Next.js Route Handlers
* Server Actions where useful
* LangGraph for agent workflows
* OpenAI API for chat, summarization, embeddings, and sentiment support

Data:

* Supabase datastore for structured data
* Qdrant Cloud for vector search

Deployment:

* Vercel
* Vercel Cron Jobs
* GitHub + Vercel CI/CD

---

# 4. Build Plan

Follow this implementation order unless the user asks otherwise.

## Phase 1: Project Setup

1. Convert the current skeleton into a Next.js 15 TypeScript app.
2. Add TailwindCSS and shadcn/ui.
3. Create a clean folder structure.
4. Add environment variable examples.
5. Add basic linting and formatting.

Recommended structure:

```text
app/
  page.tsx
  dashboard/
  assistant/
  feed/
  api/
components/
  ui/
  dashboard/
  assistant/
lib/
  supabase/
  qdrant/
  openai/
  ingestion/
  risk/
  rag/
  agent/
types/
docs/
```

## Phase 2: Supabase Data Layer

1. Create schema definitions for:
   * `regions`
   * `disruptions`
   * `documents`
2. Add Supabase client helpers.
3. Keep server-only keys on the server.
4. Build read routes for:
   * regions
   * risk scores
   * recent disruptions
   * documents

## Phase 3: Dashboard MVP

1. Build the dashboard with mock data first.
2. Add:
   * Global Risk Index
   * High Risk Regions
   * Recent Disruptions
   * Risk Trend Chart
3. Replace mock data with Supabase data.
4. Add loading, empty, and error states.

## Phase 4: Ingestion Pipeline

1. Create one ingestion route.
2. Start with News API.
3. Normalize external data into a consistent internal shape.
4. Store event metadata in Supabase.
5. Generate embeddings and store vectors in Qdrant.
6. Add OpenWeather after the news ingestion works.
7. Add optional logistics feed only after the core flow is stable.

## Phase 5: RAG Assistant

1. Create a chat API route.
2. Embed the user query.
3. Search Qdrant for related documents.
4. Load related risk scores and disruptions from Supabase.
5. Generate an answer with OpenAI.
6. Always return citations when using retrieved documents.
7. Show citations in the UI.

## Phase 6: Risk Scoring

Start with an explainable scoring model:

* Weather severity: up to 40 points
* Disruption frequency: up to 40 points
* Negative sentiment: up to 20 points

Classify risk:

* `Low`: 0 to 39
* `Medium`: 40 to 69
* `High`: 70 to 100

Store both the numeric score and classification in Supabase.

## Phase 7: Deployment

1. Add production environment variables in Vercel.
2. Deploy the Next.js app to Vercel.
3. Configure Vercel Cron for hourly ingestion.
4. Verify the dashboard loads under 3 seconds.
5. Verify chat responses complete under 8 seconds where possible.

---

# 5. Environment Variables

Use environment variables for all secrets and external services.

Expected variables:

```text
OPENAI_API_KEY=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
QDRANT_URL=
QDRANT_API_KEY=
NEWS_API_KEY=
OPENWEATHER_API_KEY=
```

Rules:

* Never commit real secrets.
* Use `.env.example` for placeholder values.
* Use `SUPABASE_SERVICE_ROLE_KEY` only in server-side code.
* Do not expose Qdrant or OpenAI keys to the browser.

---

# 6. Data Modeling Rules

Keep the MVP schema simple.

## regions

Stores region-level risk state.

Fields:

* `id`
* `name`
* `risk_score`
* `risk_level`
* `last_updated`

## disruptions

Stores chronological disruption events.

Fields:

* `id`
* `title`
* `description`
* `region`
* `severity`
* `source`
* `url`
* `created_at`

## documents

Stores metadata for content embedded in Qdrant.

Fields:

* `id`
* `title`
* `source`
* `url`
* `published_at`
* `embedding_id`

Best practices:

* Use stable IDs.
* Deduplicate documents by URL when possible.
* Store timestamps in UTC.
* Keep raw external API payloads out of the main tables unless needed for debugging.

---

# 7. AI and RAG Best Practices

The assistant must be grounded in retrieved data.

Rules:

* Retrieve context before answering operational risk questions.
* Include sources when using retrieved documents.
* Do not invent source URLs.
* If no relevant sources are found, say that the available data is limited.
* Keep answers concise and decision-focused.
* Separate facts from model interpretation.
* Prefer structured outputs from internal AI calls when possible.

Suggested response shape:

```text
Summary:
Risk Level:
Key Drivers:
Affected Regions:
Sources:
```

Prompting rules:

* Keep system prompts short and explicit.
* Pass only relevant context to the model.
* Avoid sending secrets or unnecessary metadata to OpenAI.
* Use lower temperature for factual answers.

---

# 8. Ingestion Best Practices

External APIs can fail. Design ingestion so one failed source does not break the whole job.

Rules:

* Fetch each source independently.
* Log source-level failures.
* Normalize data before storage.
* Deduplicate before inserting.
* Retry embeddings when generation fails.
* Keep ingestion idempotent so repeated cron runs do not create duplicate records.
* Do not block dashboard reads if ingestion fails.

Minimum normalized event shape:

```ts
type NormalizedDisruption = {
  title: string;
  description: string;
  region: string;
  severity: "Low" | "Medium" | "High";
  source: string;
  url?: string;
  publishedAt: string;
};
```

---

# 9. Frontend Best Practices

Build the app as a working product, not a landing page.

Rules:

* The first screen should be the dashboard experience.
* Keep the UI calm, operational, and easy to scan.
* Use cards for repeated data items, not for every page section.
* Add loading, empty, and error states for data-driven components.
* Use charts only where they clarify risk trends.
* Use clear severity colors, but do not rely on color alone.
* Make tables and feeds readable on mobile and desktop.
* Keep text inside buttons and UI elements from overflowing.

Recommended pages:

* `/` or `/dashboard`
* `/regions`
* `/assistant`
* `/feed`

---

# 10. Backend Best Practices

Rules:

* Keep API routes small.
* Put shared logic in `lib/`.
* Validate request payloads.
* Return consistent error shapes.
* Use server-side clients for OpenAI, Supabase service role, and Qdrant.
* Avoid mixing UI code with ingestion, RAG, or risk scoring logic.

Recommended API routes:

```text
app/api/regions/route.ts
app/api/disruptions/route.ts
app/api/assistant/route.ts
app/api/ingest/route.ts
app/api/risk/recalculate/route.ts
```

---

# 11. Testing and Verification

Add tests where they reduce risk.

Minimum checks:

* Risk scoring function tests
* Data normalization tests
* RAG context formatting tests
* API route validation tests where practical

Before finishing a feature:

1. Run linting.
2. Run tests if available.
3. Start the dev server for UI work.
4. Check that pages render without console errors.
5. Confirm no secrets are committed.

---

# 12. Error Handling

Use graceful degradation.

Examples:

* If News API fails, still process weather data.
* If OpenWeather fails, keep previous weather-derived scores.
* If Qdrant search fails, answer from Supabase data if possible.
* If OpenAI fails, show a clear assistant error instead of an empty response.
* If Supabase is unavailable, show dashboard error states.

---

# 13. Security Rules

Security is part of the MVP.

Rules:

* Never expose service role keys in client components.
* Never commit `.env.local`.
* Validate user input in chat and API routes.
* Keep all external service calls server-side unless a public client is explicitly safe.
* Do not store sensitive business data in the MVP.
* Do not log full API keys, user secrets, or raw authorization headers.

---

# 14. Documentation Rules

Update documentation when architecture changes.

Docs to maintain:

* `README.md`
* `docs/PRD.md`
* `docs/architecture.md`
* `AGENT.md`

When adding a major feature, update the README with:

* What the feature does
* Required environment variables
* How to run it locally

---

# 15. Definition of Done

A feature is done when:

* It matches the PRD and architecture docs.
* It has clear error handling.
* It does not expose secrets.
* It is connected to the correct data source or has clearly marked mock data.
* It has basic verification through tests, linting, or manual UI checks.
* The implementation is simple enough for a Junior AI Engineer to follow.

---

# 16. Important Constraints

For the MVP, do not build:

* User management
* ERP integration
* Supplier integration
* Predictive forecasting
* Mobile app
* Alert subscriptions

Only add these if the user explicitly changes the scope.
