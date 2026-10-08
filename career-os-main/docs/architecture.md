# Career OS Architecture

## Core loop

```
REAL JOBS
   ↓
MARKET
   ↓
SKILL EXTRACTION
   ↓
NORMALIZED SKILLS
   ↓
GAP ENGINE
   ↓
LEARN → BUILD → PROVE
   ↓
APPLICATIONS
   ↓
FEEDBACK
   ↺
```

## Initial components

- PostgreSQL + pgvector: system of record and future semantic retrieval.
- n8n: workflow orchestration and integrations.
- LLM: structured extraction and reasoning.
- GitHub: source code and Proof of Work.
- FastAPI/Python: application and API layer.

## First milestone

The first milestone is deliberately small:

1. Store a real job.
2. Extract its competencies.
3. Normalize competencies.
4. Compare them against the user's skill inventory.
5. Generate a prioritized action.
6. Persist the result.

Only after this loop works end-to-end should job acquisition and broader automation be added.
