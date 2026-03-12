# CLAUDE.md

This file is the primary memory and guidance document for Claude Code working in this repository.
Read it fully at the start of every session before making any changes.

---

## Project Purpose

This repository is a **Python monorepo for internal AI solutions for marketing teams**.
It contains agents, dashboards, workflows, and shared components built on the Anthropic Claude API.

**Tech stack:**
- Python 3.11+
- Anthropic SDK (`anthropic` package) — `claude-opus-4-6` default model
- Pydantic + Pydantic Settings — data validation and config
- Loguru — structured logging
- Streamlit — internal dashboards (MVP)
- Ruff — linting and formatting
- Pytest — testing

---

## Repository Structure

```
marketing-ai/
│
├── CLAUDE.md                              # ← you are here
├── README.md
├── pyproject.toml                         # deps, ruff, pytest config
├── .env.example                           # documented env vars (never commit .env)
│
├── agents/                                # Autonomous AI agents
│   └── content_writer/
│       ├── agent.py                       # Orchestration + agentic loop
│       ├── tools.py                       # Tool definitions and executors
│       ├── prompts.py                     # Prompt loader from prompts/
│       └── tests/
│           └── test_tools.py
│
├── dashboards/                            # Streamlit UIs
│   └── agent_monitor/
│       └── app.py                         # Run: streamlit run dashboards/agent_monitor/app.py
│
├── workflows/                             # Multi-step pipelines (add here)
│
├── components/                            # Shared reusable code
│   ├── llm/
│   │   ├── client.py                      # THE only Anthropic client wrapper
│   │   ├── retry.py                       # Exponential backoff decorator
│   │   └── structured_output.py           # Pydantic-based response parsing
│   ├── data/                              # CRM, analytics adapters (add here)
│   ├── ui/                                # Shared Streamlit components (add here)
│   └── utils/
│       └── logging.py                     # Loguru setup — always use get_logger()
│
├── prompts/                               # All prompt templates, versioned as files
│   ├── system/
│   │   └── marketing_assistant.md         # Base system prompt for all agents
│   ├── memory/
│   │   ├── brand_voice.md                 # Brand guidelines (fill in)
│   │   └── audience_personas.md           # Audience personas (fill in)
│   └── tasks/
│       ├── write_blog_post.md
│       └── analyse_campaign.md
│
├── config/
│   ├── settings.py                        # Pydantic Settings — all env vars here
│   ├── models.py                          # LLM model aliases and metadata
│   └── feature_flags.py                   # Feature flag helpers
│
├── docs/
│   └── decisions/                         # Architecture decision records (ADRs)
│       └── 2026-03-12-monorepo-python.md
│
└── tests/
    └── conftest.py                        # Shared pytest fixtures
```

---

## Critical Rules

### 1. Single LLM client
**Never** instantiate `anthropic.Anthropic()` directly. Always use:
```python
from components.llm import get_client
client = get_client()
```

### 2. Single config entry point
**Never** call `os.getenv()` directly. Always use:
```python
from config import get_settings
settings = get_settings()
```

### 3. Single logger entry point
**Never** use `print()` in production code. Always use:
```python
from components.utils.logging import get_logger
logger = get_logger(__name__)
logger.info("event_name", key="value")
```

### 4. Prompts are files, not strings
All LLM prompts live in `prompts/` as Markdown files. Load them via the agent's
`prompts.py` module — never hardcode prompt strings in agent or workflow code.

### 5. Agents default to dry_run=True
Any agent or tool that writes files or calls external systems must support a `dry_run` flag.
New agents default to `dry_run=True` until explicitly tested and approved.

### 6. Tools are standalone functions
Tools in `tools.py` must not call other agents and must not hold state.
Each tool is a pure function: input → output. Side effects (file writes) are
the tool's explicit purpose and must be guarded by `dry_run`.

---

## Coding Standards

- Python 3.11+ — use `match/case`, `X | Y` union types, `TypeAlias`, etc.
- `ruff check .` and `ruff format .` must pass before every commit.
- All function signatures and return types must be annotated.
- Use `pydantic` models for structured data — no raw dicts for domain objects.
- Use `async def` for I/O-bound operations (LLM calls, API calls, DB queries).
- No comments explaining *what* the code does — only *why* when non-obvious.
- No `# FIXME` or `# TODO` without a linked issue. Fix it or delete it.

---

## LLM Usage

### Default model
```python
from config.models import DEFAULT_MODEL
# DEFAULT_MODEL.id == "claude-opus-4-6"
```

### Standard call
```python
response = client.messages.create(
    model=DEFAULT_MODEL.id,
    max_tokens=4096,
    system=system_prompt,
    messages=messages,
)
```

### For thinking / complex reasoning
```python
response = client.messages.create(
    model=DEFAULT_MODEL.id,
    max_tokens=8192,
    thinking={"type": "adaptive"},
    messages=messages,
)
```

### For streaming (max_tokens > 4096 or latency-sensitive)
```python
with client.messages.stream(model=..., max_tokens=..., messages=...) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final = stream.get_final_message()
```

### For structured output
```python
from components.llm.structured_output import parse_response
result: MyModel = parse_response(client, MyModel, model=..., messages=...)
```

---

## Testing Conventions

| Layer | Requirement |
|-------|------------|
| `components/` | Unit tests for all public functions (no LLM calls) |
| `agents/` tools | Unit tests with real filesystem via `tmp_path` |
| `agents/` agent | Integration test with mocked LLM (`unittest.mock.patch`) |
| `workflows/` | Integration test per pipeline step; E2E for happy path |
| `dashboards/` | No automated tests for Streamlit MVP; add when migrating to FastAPI |

- Always mock external calls (LLM, CRM, analytics) in unit and integration tests.
- Use `pytest` fixtures from `tests/conftest.py` — don't duplicate setup.
- Use `fake_api_key` fixture when tests need Settings to load (avoids .env dependency).
- Target >80% coverage for `components/`.

---

## Documenting Assumptions

When code relies on a non-obvious assumption:

1. **Inline**: `# ASSUMPTION: the CRM API is the source of truth for contact data`
2. **In commits**: mention key assumptions in the commit body
3. **In ADRs**: for architectural decisions, add a file to `docs/decisions/YYYY-MM-DD-slug.md`

---

## Reusable Components Rules

1. Extract to `components/` only when a second use case appears.
2. Every component must be fully typed.
3. Utilities in `components/utils/` must be pure (no I/O, no global state mutation).
4. Every public function in `components/` must have a unit test.
5. Add a docstring explaining inputs, outputs, and any exceptions raised.

---

## Adding a New Agent

1. Create `agents/<agent_name>/` with `agent.py`, `tools.py`, `prompts.py`, `tests/`.
2. Add a feature flag in `config/settings.py` and `.env.example`.
3. Add the task prompt template in `prompts/tasks/<task_name>.md`.
4. Implement with `dry_run=True` default.
5. Write unit tests for all tools before opening a PR.
6. Add the agent to the dashboard tab list in `dashboards/agent_monitor/app.py`.

---

## Git and Branch Conventions

| Branch | Purpose |
|--------|---------|
| `master` | Default — production-ready |
| `feature/<slug>` | New features |
| `fix/<slug>` | Bug fixes |
| `claude/<session-id>-<slug>` | AI assistant branches |

Commit messages: imperative mood, present tense (`Add campaign analyst agent`).
Include context in the body for non-obvious changes.

---

## Environment Configuration

- Copy `.env.example` → `.env` for local development — **never commit `.env`**.
- Every new env var must be documented in `.env.example` with a comment.
- Load all vars through `config/settings.py` — never `os.getenv()` elsewhere.

---

## Key Reminders for Claude Code Sessions

- **Read this file first** before writing any code.
- **Read the relevant files** before editing — never guess existing structure.
- **Do not over-engineer**: implement the minimum for the current task.
- **Do not add docstrings or comments** to code you didn't change.
- **Prefer editing existing files** over creating new ones.
- **Document decisions** in `docs/decisions/` if making a non-obvious architectural choice.
- **Run `ruff check .` mentally** — avoid unused imports, undefined names, wrong types.
