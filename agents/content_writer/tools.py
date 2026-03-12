"""Tools available to the content writer agent.

Each tool is a standalone, typed function. Tools must not call other agents
and must not have side effects unless that side effect is the tool's explicit purpose.

These tools are wired into the agent via the Anthropic tool use API.
"""

import json
from pathlib import Path

from pydantic import BaseModel

from components.utils.logging import get_logger

logger = get_logger(__name__)

# ── Tool input/output models ───────────────────────────────────────────────────


class BrandGuidelinesResult(BaseModel):
    voice: str
    tone_attributes: list[str]
    avoid: list[str]


class ToneCheckResult(BaseModel):
    on_brand: bool
    score: float  # 0.0 – 1.0
    issues: list[str]
    suggestions: list[str]


# ── Tool definitions (JSON schema for the API) ─────────────────────────────────

TOOLS: list[dict] = [
    {
        "name": "get_brand_guidelines",
        "description": (
            "Retrieve the brand voice guidelines and writing rules. "
            "Call this before drafting any content to ensure brand consistency."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "channel": {
                    "type": "string",
                    "description": "The distribution channel (blog, linkedin, twitter, email, ad)",
                    "enum": ["blog", "linkedin", "twitter", "email", "ad"],
                }
            },
            "required": ["channel"],
        },
    },
    {
        "name": "get_audience_persona",
        "description": (
            "Retrieve the detailed profile for a target audience persona. "
            "Use this to tailor tone, complexity, and messaging."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "persona_name": {
                    "type": "string",
                    "description": "The persona name (e.g., 'Marketing Manager', 'CMO')",
                }
            },
            "required": ["persona_name"],
        },
    },
    {
        "name": "save_draft",
        "description": (
            "Save a content draft to a local file for human review. "
            "Always call this after producing a final draft."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Output filename (e.g., 'blog-post-ai-marketing.md')",
                },
                "content": {
                    "type": "string",
                    "description": "The full content to save",
                },
            },
            "required": ["filename", "content"],
        },
    },
]


# ── Tool execution functions ───────────────────────────────────────────────────


def get_brand_guidelines(channel: str) -> str:
    """Return brand voice guidelines for the given channel."""
    brand_voice_path = Path(__file__).parent.parent.parent / "prompts" / "memory" / "brand_voice.md"
    guidelines = brand_voice_path.read_text(encoding="utf-8")

    logger.debug("tool_get_brand_guidelines", channel=channel)
    return json.dumps({
        "channel": channel,
        "guidelines": guidelines,
        "note": f"Pay special attention to the '{channel}' row in the 'Tone by Channel' table.",
    })


def get_audience_persona(persona_name: str) -> str:
    """Return the persona profile matching the given name."""
    personas_path = (
        Path(__file__).parent.parent.parent / "prompts" / "memory" / "audience_personas.md"
    )
    personas_text = personas_path.read_text(encoding="utf-8")

    logger.debug("tool_get_audience_persona", persona=persona_name)
    return json.dumps({
        "persona_name": persona_name,
        "personas_doc": personas_text,
        "note": "Use the persona that best matches the requested name.",
    })


def save_draft(filename: str, content: str, dry_run: bool = False) -> str:
    """Save a content draft to the outputs/ directory."""
    output_dir = Path("outputs") / "drafts"
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = Path(filename).name  # prevent path traversal
    output_path = output_dir / safe_filename

    if dry_run:
        logger.info("tool_save_draft_dry_run", path=str(output_path), chars=len(content))
        return json.dumps({"dry_run": True, "would_save_to": str(output_path)})

    output_path.write_text(content, encoding="utf-8")
    logger.info("tool_save_draft", path=str(output_path), chars=len(content))
    return json.dumps({"saved_to": str(output_path), "chars": len(content)})


# ── Dispatcher ─────────────────────────────────────────────────────────────────

def execute_tool(name: str, tool_input: dict, dry_run: bool = False) -> str:
    """Route a tool call from the agent to the correct function."""
    match name:
        case "get_brand_guidelines":
            return get_brand_guidelines(**tool_input)
        case "get_audience_persona":
            return get_audience_persona(**tool_input)
        case "save_draft":
            return save_draft(**tool_input, dry_run=dry_run)
        case _:
            raise ValueError(f"Unknown tool: '{name}'")
