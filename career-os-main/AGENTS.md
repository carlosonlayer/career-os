# Career OS — Agent Instructions

## Mission
Build Career OS as a market-driven AI Engineering career operating system.

## Engineering principles
- Prefer working software over speculative complexity.
- Market evidence drives the backlog.
- Every learning task should produce verifiable Proof of Work.
- Never invent job requirements or market evidence.
- Keep private/personal data out of source control.
- Use small, testable modules.
- Document architectural decisions.
- Add tests for deterministic business logic.
- Human review is required before destructive or production-impacting actions.

## Initial stack
- Python
- FastAPI
- PostgreSQL
- pgvector
- Docker
- n8n
- GitHub
- LLM APIs

## Initial architecture
Jobs -> extraction -> normalized skills -> skill inventory -> gap engine -> learning/build/proof backlog -> applications -> feedback.

## Coding conventions
- Python 3.12+
- Type hints
- pytest
- environment variables for secrets
- no hard-coded API keys
