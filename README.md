# Marketing AI

Internal AI solutions for marketing teams — agents, dashboards, workflows, and shared components built on the Anthropic Claude API.

## Quick Start

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Configure environment
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY

# 3. Run linter
ruff check . && ruff format --check .

# 4. Run tests
pytest
```

## Structure

```
agents/          Autonomous AI agents (content writer, campaign analyst, …)
dashboards/      Streamlit UIs for metrics and agent monitoring
workflows/       Multi-step orchestrated pipelines
components/      Shared reusable code (LLM client, data adapters, utils)
prompts/         Versioned prompt templates and memory files
config/          Centralised configuration and feature flags
docs/            Architecture decisions and runbooks
```

## Available Agents

| Agent | Status | Description |
|-------|--------|-------------|
| `content_writer` | Active | Drafts blog posts and social content |
| `campaign_analyst` | Planned | Analyses campaign performance |
| `lead_scorer` | Planned | Scores inbound leads |

## Running a Dashboard

```bash
streamlit run dashboards/agent_monitor/app.py
```

## Development

- Lint: `ruff check .`
- Format: `ruff format .`
- Test: `pytest`
- Coverage: `pytest --cov`

See [CLAUDE.md](CLAUDE.md) for full development conventions.
