"""Prompt loader for the content writer agent.

Prompts live in prompts/ as Markdown files. This module loads them at import time
so any missing file is caught immediately at startup, not mid-run.
"""

from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def _load(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


# ── Loaded at import time ──────────────────────────────────────────────────────

SYSTEM_PROMPT: str = _load(_PROMPTS_DIR / "system" / "marketing_assistant.md")

BRAND_VOICE: str = _load(_PROMPTS_DIR / "memory" / "brand_voice.md")

AUDIENCE_PERSONAS: str = _load(_PROMPTS_DIR / "memory" / "audience_personas.md")

WRITE_BLOG_POST_TEMPLATE: str = _load(_PROMPTS_DIR / "tasks" / "write_blog_post.md")


def build_system_prompt() -> str:
    """Compose the full system prompt injected into every content writer call."""
    return "\n\n---\n\n".join([
        SYSTEM_PROMPT,
        "## Brand Voice\n\n" + BRAND_VOICE,
        "## Audience Personas\n\n" + AUDIENCE_PERSONAS,
    ])


def build_write_blog_post_prompt(
    topic: str,
    target_audience: str,
    word_count: int = 800,
    keywords: str = "",
    tone_notes: str = "follow brand voice guidelines",
) -> str:
    """Fill in the blog post task template."""
    return WRITE_BLOG_POST_TEMPLATE.format(
        topic=topic,
        target_audience=target_audience,
        word_count=word_count,
        keywords=keywords or "none specified",
        tone_notes=tone_notes,
    )
