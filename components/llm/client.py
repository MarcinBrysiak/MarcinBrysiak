"""Single Anthropic client wrapper — the only place in the codebase that
instantiates an Anthropic client.

All agents and workflows must use get_client() instead of creating their own
anthropic.Anthropic() instances. This ensures consistent configuration,
logging, and token tracking across the entire codebase.

Usage:
    from components.llm import get_client

    client = get_client()
    response = client.messages.create(
        model=DEFAULT_MODEL.id,
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello"}],
    )

For streaming (use for max_tokens > 4096 or latency-sensitive output):
    with client.messages.stream(...) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        final = stream.get_final_message()

For structured output (Pydantic model):
    from components.llm.structured_output import parse_response
    result = parse_response(client, MyModel, messages=[...])
"""

from functools import lru_cache

import anthropic

from components.utils.logging import get_logger
from config.settings import get_settings

logger = get_logger(__name__)


class LLMClient:
    """Thin wrapper around anthropic.Anthropic that adds logging and token tracking."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._async_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    @property
    def messages(self):
        """Direct access to the sync Messages API."""
        return _LoggingMessages(self._client.messages)

    @property
    def async_messages(self):
        """Direct access to the async Messages API."""
        return self._async_client.messages

    @property
    def beta(self):
        """Access to beta APIs (structured output via .messages.parse, etc.)."""
        return self._client.beta


class _LoggingMessages:
    """Wraps the Messages API to log token usage on every call."""

    def __init__(self, messages) -> None:
        self._messages = messages

    def create(self, **kwargs) -> anthropic.types.Message:
        response = self._messages.create(**kwargs)
        _log_usage(response, kwargs.get("model", "unknown"))
        return response

    def stream(self, **kwargs):
        """Return a streaming context manager. Caller is responsible for logging usage."""
        return self._messages.stream(**kwargs)

    def parse(self, **kwargs):
        """Structured output via client.messages.parse()."""
        return self._messages.parse(**kwargs)

    def count_tokens(self, **kwargs):
        return self._messages.count_tokens(**kwargs)


def _log_usage(response: anthropic.types.Message, model: str) -> None:
    usage = response.usage
    logger.debug(
        "llm_call",
        model=model,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        stop_reason=response.stop_reason,
    )


@lru_cache(maxsize=1)
def get_client() -> LLMClient:
    """Return the singleton LLMClient.

    Cached after first call. Call get_client.cache_clear() in tests to reset.
    """
    return LLMClient()
