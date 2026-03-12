"""Content Writer Agent.

Orchestrates the LLM + tools to produce marketing content drafts.
Supports dry_run mode — no files are written, no external systems are called.

Usage:
    from agents.content_writer import ContentWriterAgent

    agent = ContentWriterAgent(dry_run=True)
    result = agent.write_blog_post(
        topic="How AI is transforming B2B marketing",
        target_audience="Marketing Manager",
        word_count=800,
        keywords="AI marketing, marketing automation, B2B content",
    )
    print(result.content)
"""

from dataclasses import dataclass, field

import anthropic

from agents.content_writer.prompts import build_system_prompt, build_write_blog_post_prompt
from agents.content_writer.tools import TOOLS, execute_tool
from components.llm import get_client
from components.utils.logging import get_logger
from config.models import DEFAULT_MODEL

logger = get_logger(__name__)

# Safety limit — prevents runaway loops
_MAX_TOOL_ITERATIONS = 10


@dataclass
class ContentDraft:
    topic: str
    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    tool_calls: list[str] = field(default_factory=list)
    dry_run: bool = False


class ContentWriterAgent:
    """Agent that produces marketing content drafts using tool-augmented LLM calls."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL.id,
        dry_run: bool = False,
    ) -> None:
        self._model = model
        self._dry_run = dry_run
        self._client = get_client()

        if dry_run:
            logger.info("content_writer_dry_run_mode", model=model)

    def write_blog_post(
        self,
        topic: str,
        target_audience: str,
        word_count: int = 800,
        keywords: str = "",
        tone_notes: str = "",
    ) -> ContentDraft:
        """Generate a blog post draft.

        Args:
            topic: The blog post topic or title idea.
            target_audience: Which persona to target (must match audience_personas.md).
            word_count: Target word count.
            keywords: SEO keywords to include, comma-separated.
            tone_notes: Additional tone guidance beyond brand voice baseline.

        Returns:
            ContentDraft with the generated content and metadata.
        """
        logger.info(
            "content_writer_start",
            topic=topic,
            audience=target_audience,
            dry_run=self._dry_run,
        )

        system = build_system_prompt()
        user_message = build_write_blog_post_prompt(
            topic=topic,
            target_audience=target_audience,
            word_count=word_count,
            keywords=keywords,
            tone_notes=tone_notes,
        )

        messages: list[dict] = [{"role": "user", "content": user_message}]
        total_input_tokens = 0
        total_output_tokens = 0
        tool_calls_made: list[str] = []

        # Agentic loop — keep going until the model stops calling tools
        for iteration in range(_MAX_TOOL_ITERATIONS):
            response = self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                system=system,
                tools=TOOLS,
                messages=messages,
            )

            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens

            if response.stop_reason == "end_turn":
                break

            if response.stop_reason != "tool_use":
                logger.warning(
                    "content_writer_unexpected_stop",
                    stop_reason=response.stop_reason,
                    iteration=iteration,
                )
                break

            # Append assistant response to history
            messages.append({"role": "assistant", "content": response.content})

            # Execute all tool calls and collect results
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                tool_calls_made.append(block.name)
                logger.debug("content_writer_tool_call", tool=block.name, input=block.input)

                result = execute_tool(block.name, block.input, dry_run=self._dry_run)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

            messages.append({"role": "user", "content": tool_results})
        else:
            logger.error(
                "content_writer_max_iterations",
                max=_MAX_TOOL_ITERATIONS,
                topic=topic,
            )

        # Extract the final text from the last response
        final_text = "\n\n".join(
            block.text for block in response.content if block.type == "text"
        )

        logger.info(
            "content_writer_done",
            topic=topic,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            tool_calls=tool_calls_made,
            dry_run=self._dry_run,
        )

        return ContentDraft(
            topic=topic,
            content=final_text,
            model=self._model,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            tool_calls=tool_calls_made,
            dry_run=self._dry_run,
        )
