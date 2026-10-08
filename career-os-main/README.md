# Career OS — Market-Driven AI Engineering OS

Career OS works without a paid LLM API. The default pipeline is deterministic and local. An LLM is an optional provider, not a runtime dependency.

## Run locally

1. Copy .env.example to .env.
2. Keep LLM_PROVIDER=none.
3. Run:

```bash
docker compose up -d --build
```

Services:
- API: http://localhost:8000
- n8n: http://localhost:5678
- PostgreSQL: localhost:5432

## Job intake

POST /jobs/intake with a real job description.

With LLM_PROVIDER=none, the extractor detects only skills explicitly present, normalizes known variants, stores surrounding evidence, and updates market demand.

## Gap Engine

After intake, call GET /jobs/{job_id}/gap.

It combines required/optional signal, market frequency, current level, target level and Proof-of-Work evidence. Missing user levels are treated as unvalidated, not as a claim of zero ability.

For each gap it creates a build-oriented learning task with implementation, tests, documentation, commit and publishable evidence.

## Optional OpenAI

OpenAI is optional. Install api/requirements-openai.txt only when paid API usage is acceptable, set LLM_PROVIDER=openai and provide OPENAI_API_KEY.

## n8n

Import n8n/workflow-job-intake.json into the local n8n instance.

## Security

Never commit .env. API keys belong only in environment variables or n8n credentials.

## Current scope

Implemented:
- zero-cost job intake and skill extraction;
- optional LLM provider;
- PostgreSQL persistence;
- market demand counters;
- deterministic Gap Engine;
- Proof-of-Work task generation.

Next:
- real job collection/search;
- 10–20 job calibration set;
- skill inventory validation;
- project-to-skill proof mapping;
- applications and feedback.
