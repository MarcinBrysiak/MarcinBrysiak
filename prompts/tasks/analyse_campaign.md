# Task: Analyse Campaign Performance

## Input Variables

- `{campaign_name}` — name of the campaign
- `{date_range}` — reporting period (e.g., "Q1 2026")
- `{metrics_data}` — raw metrics (JSON or table)
- `{goal}` — primary campaign goal (awareness / leads / revenue)
- `{benchmark}` — industry benchmark or previous period for comparison

## Prompt Template

Analyse the performance of campaign **{campaign_name}** for the period **{date_range}**.

Campaign goal: {goal}

Metrics data:
```
{metrics_data}
```

Benchmark for comparison: {benchmark}

Produce a structured analysis with the following sections:

1. **Executive Summary** (3 sentences max — suitable for a CMO)
2. **Performance vs Goal** — did we hit the target? By how much?
3. **What Worked** — top 2–3 performing elements with evidence
4. **What Didn't Work** — top 2–3 underperforming elements with root cause hypothesis
5. **Anomalies** — any unexpected spikes or drops worth investigating
6. **Suggested Next Steps** — 3 concrete, prioritised actions

For every claim, cite the specific metric that supports it.
Mark any assumption clearly with: **ASSUMPTION**: [text]
