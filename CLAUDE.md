# CLAUDE.md

This file is the primary memory and guidance document for Claude Code working in this repository. Read it fully at the start of every session before making any changes.

---

## Project Purpose

This repository houses **internal AI solutions for marketing teams**, including:

- **Agents** — autonomous or semi-autonomous AI workflows (e.g., content generation, campaign analysis, lead scoring)
- **Dashboards** — data-driven UIs for visualising marketing metrics and agent outputs
- **Workflows** — orchestrated multi-step pipelines connecting tools, APIs, and AI models
- **Reusable components** — shared UI components, utility functions, prompt templates, and service clients used across features

The goal is a structured, maintainable monorepo that scales as the marketing AI surface grows — not a collection of one-off scripts.

---

## Expected Architecture Discipline

- **Separation of concerns**: business logic, AI/LLM calls, data access, and UI are distinct layers. Never mix them in a single file.
- **Thin agents, rich tools**: agents should orchestrate tools — they should not contain business logic themselves.
- **No magic globals**: pass configuration explicitly; avoid relying on ambient module-level state.
- **Async by default**: all I/O-bound operations (API calls, DB queries, LLM calls) must be `async`.
- **Fail loudly**: prefer explicit errors over silent fallbacks. Log and surface failures; do not swallow exceptions.
- **Stateless where possible**: prefer pure functions and stateless service classes. Persist state explicitly (DB, cache, file).

---

## Folder Structure Guidance

```
/
├── agents/               # Individual AI agent definitions
│   └── <agent-name>/
│       ├── agent.py      # Agent entrypoint and orchestration logic
│       ├── tools.py      # Tools/functions the agent can call
│       ├── prompts.py    # Prompt templates for the agent
│       └── tests/
├── dashboards/           # Dashboard applications (e.g. Streamlit, Next.js)
│   └── <dashboard-name>/
├── workflows/            # Multi-step pipeline definitions
│   └── <workflow-name>/
├── components/           # Reusable shared code
│   ├── llm/              # LLM client wrappers, prompt utilities
│   ├── data/             # Data access and transformation helpers
│   ├── ui/               # Shared UI components
│   └── utils/            # General utilities (logging, config, validation)
├── config/               # Environment configuration and constants
├── tests/                # Top-level integration and E2E tests
├── docs/                 # Architecture decisions, runbooks, design notes
└── CLAUDE.md             # This file
```

- New features belong in their respective top-level directory (`agents/`, `dashboards/`, `workflows/`).
- Anything used by more than one feature goes into `components/`.
- Never create files directly at the repo root except for project-wide config (`.env.example`, `pyproject.toml`, `package.json`, etc.).

---

## Coding Standards

### Python

- Python 3.11+.
- Use `ruff` for linting and formatting (`ruff check .` and `ruff format .`).
- Type-annotate all function signatures and return types.
- Use `pydantic` models for data validation and structured LLM output.
- Prefer `httpx` over `requests` for HTTP calls.
- Use `loguru` or the standard `logging` module — never `print()` in production code.

### JavaScript / TypeScript

- TypeScript strict mode enabled.
- Use `eslint` + `prettier` for linting and formatting.
- Functional components with hooks for React/Next.js UIs.
- No `any` types; use `unknown` and narrow explicitly.

### General

- **No hardcoded secrets or credentials** — use environment variables loaded via `dotenv` or a secrets manager. Add secrets to `.gitignore` and document them in `.env.example`.
- **No commented-out dead code** — delete it; git history preserves old code.
- Keep functions and files small and focused. A function longer than ~50 lines is a signal to refactor.

---

## Documenting Assumptions

When code relies on an assumption that is not immediately obvious from context, document it explicitly:

1. **In code**: add an inline comment starting with `# ASSUMPTION:` or `// ASSUMPTION:` that states what is assumed and why.
2. **In commits**: mention key assumptions in the commit message body.
3. **In `docs/`**: for architectural assumptions (e.g., "we assume the CRM API is the source of truth for contact data"), create or update a file in `docs/decisions/` using the format `YYYY-MM-DD-<short-slug>.md`.

Never leave implicit assumptions — they are the most common source of bugs when requirements change.

---

## Reusable Components — Rules

1. **Promote early**: if you write the same logic twice, extract it into `components/` before the third use.
2. **Single responsibility**: one component does one thing. Do not bundle unrelated utilities.
3. **Typed interfaces**: every reusable function or class must have fully typed inputs and outputs.
4. **No side effects in utilities**: utility functions in `components/utils/` must be pure — no I/O, no logging, no global mutation.
5. **Tests required**: every component in `components/` must have unit tests. Do not add a component without tests.
6. **Document the contract**: add a docstring explaining what the component does, its parameters, return value, and any exceptions it raises.

---

## AI Agents — Guidance

- **Define tools as typed functions**: each tool the agent can call must be a standalone, typed function with a clear docstring. Tools must not call other agents.
- **Prompt templates in `prompts.py`**: keep all prompts versioned and out of business logic. Use f-strings or template classes — never string concatenation scattered through agent code.
- **Limit agent autonomy by default**: agents should confirm before taking irreversible actions (sending emails, posting content, modifying CRM records). Add a `dry_run: bool` flag to agents that perform external writes.
- **Structured output**: use `pydantic` models to parse and validate all LLM responses. Never trust raw LLM text directly in downstream logic.
- **Token budget awareness**: set explicit `max_tokens` limits. Log token usage per run for monitoring.
- **Retry with backoff**: wrap LLM calls with exponential backoff and a maximum retry limit (3 retries, 2s/4s/8s).

---

## Dashboard Features — Guidance

- **Separate data fetching from rendering**: data loading logic lives in a service or hook, not in the component/page.
- **Loading and error states are mandatory**: every data-fetching view must handle loading, error, and empty states explicitly.
- **No business logic in templates/views**: dashboards display data; they do not compute it.
- **Accessibility**: use semantic HTML; ensure dashboards are keyboard-navigable.
- **Responsiveness**: all dashboard layouts must work at 1280px+ desktop widths as a minimum.

---

## Testing Expectations

| Layer | Requirement |
|-------|------------|
| `components/` | Unit tests required for all public functions/classes |
| `agents/` | Unit tests for tools; integration tests for the full agent loop (with LLM mocked) |
| `workflows/` | Integration tests for each pipeline step; E2E test for the happy path |
| `dashboards/` | Component tests for shared UI; E2E smoke test for each dashboard page |

- **Mock all external services** (LLM APIs, CRM, analytics platforms) in unit and integration tests.
- Tests live in a `tests/` subdirectory co-located with the feature, or at the top-level `tests/` for cross-cutting integration tests.
- Use `pytest` for Python. Use `vitest` or `jest` for TypeScript.
- Tests must pass locally before opening a PR. Do not push broken tests.
- Target **>80% coverage** for `components/`; aim for meaningful tests, not coverage gaming.

---

## Safe Iteration Rules

1. **Read before writing**: always read the relevant files before editing. Do not guess existing structure.
2. **One concern per PR**: keep pull requests focused. A PR that adds an agent should not also refactor the dashboard.
3. **No silent breaking changes**: if you change a shared component interface, search for all callers and update them in the same PR.
4. **Dry-run first for destructive operations**: agents or scripts that write to external systems must support a `--dry-run` flag that logs what would happen without executing it.
5. **Environment parity**: code that works in `development` must work in `production`. Avoid dev-only hacks that reach production.
6. **Feature flags for incomplete work**: if a feature is partially implemented, gate it behind a feature flag rather than merging broken or untested code to `master`.

---

## Git and Branch Conventions

- Default branch: `master`
- Feature branches: `feature/<short-description>`
- Bugfix branches: `fix/<short-description>`
- AI assistant branches: `claude/<session-id>-<short-description>`
- Commit messages: imperative mood, present tense (`Add campaign agent`, not `Added` or `Adding`). Include context in the body for non-obvious changes.
- PRs require a short description of what changed, why, and any assumptions made.

---

## Environment Configuration

- Copy `.env.example` to `.env` for local development — never commit `.env`.
- Document every required environment variable in `.env.example` with a comment explaining its purpose.
- Use a `config/` module to centralise env-var loading; do not call `os.getenv()` scattered throughout the codebase.

---

## Key Reminders for Claude Code Sessions

- **Start by reading this file** and any relevant files in `docs/` before writing code.
- **Do not over-engineer**: implement the minimum needed for the current task; extract abstractions only when there is a clear, immediate benefit.
- **Ask before deleting**: if you encounter unfamiliar files or structure, investigate before removing anything.
- **Prefer editing existing files** over creating new ones unless a new file is clearly warranted by the folder structure rules above.
- **Document decisions**: if you make a non-obvious architectural choice, add a note to `docs/decisions/`.
