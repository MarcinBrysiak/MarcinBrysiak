# ADR: Python monorepo for marketing AI tools

**Date**: 2026-03-12
**Status**: Accepted

## Context

We are starting a greenfield project to build internal AI tools for a marketing team.
We need to decide on the repository strategy and primary language.

## Decision

**Single Python monorepo** with the following structure:
- `agents/` — autonomous AI agents
- `dashboards/` — Streamlit UIs
- `workflows/` — orchestrated pipelines
- `components/` — shared reusable code
- `prompts/` — versioned prompt templates

**Python 3.11+** as the primary language.
**Anthropic Claude API** (`claude-opus-4-6` default) as the LLM backend.
**Streamlit** for dashboards (MVP speed; migrate to FastAPI+React if needed later).

## Rationale

- **Monorepo**: At this scale and team size, a single repo lowers friction for
  shared component reuse, cross-feature refactoring, and CI/CD setup.
- **Python**: Best ecosystem for AI/ML tooling (Pydantic, LangChain, data libs).
  The Anthropic Python SDK is first-class and well-maintained.
- **Streamlit**: Fastest path to a usable internal UI without frontend expertise.
  We accept the constraint that Streamlit UIs are less customisable — a trade-off
  justified at MVP stage.
- **Single LLM provider**: Starting with Anthropic only. The `components/llm/client.py`
  abstraction allows switching providers later without touching agent code.

## Consequences

- Adding a TypeScript/React frontend later would require either keeping Streamlit
  alongside or a migration effort.
- All agents share the same Python version and dependency set — a constraint that
  simplifies CI but means a single breaking dep update affects everything.
- The monorepo will need a clear ownership model as the team grows.

## Alternatives Considered

| Option | Rejected because |
|--------|-----------------|
| Multi-repo (one per agent) | Too much overhead for a small team |
| TypeScript primary | Weaker AI/ML ecosystem; team is more Python-fluent |
| OpenAI API | Anthropic Claude preferred for reasoning quality and safety |
| FastAPI+React dashboard | Too much frontend investment for MVP; revisit at scale |
