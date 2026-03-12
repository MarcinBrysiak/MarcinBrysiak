"""Structured output helpers using Pydantic models.

Wraps client.messages.parse() which validates responses against a schema
automatically. Always use this over manual JSON parsing.

Usage:
    from pydantic import BaseModel
    from components.llm.structured_output import parse_response
    from components.llm import get_client
    from config.models import DEFAULT_MODEL

    class CampaignSummary(BaseModel):
        headline: str
        key_metrics: list[str]
        recommendation: str

    client = get_client()
    result: CampaignSummary = parse_response(
        client=client,
        output_model=CampaignSummary,
        model=DEFAULT_MODEL.id,
        max_tokens=1024,
        messages=[{"role": "user", "content": "Summarise this campaign..."}],
    )
    print(result.headline)
"""

from typing import Type, TypeVar

from pydantic import BaseModel

from components.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


def parse_response(
    client,
    output_model: Type[T],
    messages: list[dict],
    model: str,
    max_tokens: int = 1024,
    system: str | None = None,
    **kwargs,
) -> T:
    """Call the Messages API and parse the response into a Pydantic model.

    Raises:
        anthropic.BadRequestError: if the schema is invalid.
        pydantic.ValidationError: if the response doesn't match the model
            (shouldn't happen with structured outputs, but guard anyway).
    """
    create_kwargs = dict(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
        output_format=output_model,
        **kwargs,
    )
    if system:
        create_kwargs["system"] = system

    response = client.beta.messages.parse(**create_kwargs)

    parsed = response.parsed_output
    if parsed is None:
        # stop_reason == "refusal" — model declined
        logger.warning(
            "structured_output_refusal",
            model=model,
            stop_reason=response.stop_reason,
        )
        raise ValueError(
            f"Model refused to produce structured output (stop_reason={response.stop_reason})"
        )

    logger.debug(
        "structured_output_ok",
        model=model,
        output_type=output_model.__name__,
    )
    return parsed
