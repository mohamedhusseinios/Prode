"""Streaming API logic for each research stage.

Supports two provider backends:
  - "anthropic" — Anthropic SDK with claude-sonnet-4-6 + built-in web search
  - "ollama"    — OpenAI-compatible API (local Ollama or any custom endpoint)
"""

from dataclasses import dataclass
from typing import AsyncGenerator, Optional

# ─── Prompts ──────────────────────────────────────────────────────────────────

_BASE_PROMPT = (
    "You are a senior product strategist with 15 years of experience building and advising "
    "B2B and B2C companies. Be specific, data-driven, and opinionated. "
    "Use real company names, real pricing when known. Format output in clean markdown "
    "with tables where useful. "
    "Don't hedge — give your actual opinion."
)

# Anthropic variant asks the model to use its built-in web search tool
ANTHROPIC_SYSTEM_PROMPT = _BASE_PROMPT + (
    " Search the web to ground your findings in current data."
)

# Ollama / local models don't have web search — keep the prompt clean
OLLAMA_SYSTEM_PROMPT = _BASE_PROMPT

MODEL_ANTHROPIC = "claude-sonnet-4-6"
MAX_TOKENS = 8096


# ─── Provider config ──────────────────────────────────────────────────────────


@dataclass
class ProviderConfig:
    """Holds everything needed to connect to an AI backend."""

    provider: str  # "anthropic" | "ollama"
    model: str = ""
    api_key: Optional[str] = None
    base_url: Optional[str] = None  # Ollama: full base URL incl. /v1

    @property
    def effective_model(self) -> str:
        return self.model or (MODEL_ANTHROPIC if self.provider == "anthropic" else "llama3.2")

    @property
    def ollama_base_url(self) -> str:
        url = self.base_url or "http://localhost:11434/v1"
        # Ensure /v1 suffix
        if not url.rstrip("/").endswith("/v1"):
            url = url.rstrip("/") + "/v1"
        return url

    @property
    def display_name(self) -> str:
        if self.provider == "anthropic":
            return f"Anthropic · {self.effective_model}"
        loc = self.base_url or "localhost:11434"
        return f"Ollama · {self.effective_model} @ {loc}"

    @property
    def has_web_search(self) -> bool:
        return self.provider == "anthropic"


# ─── Anthropic backend ────────────────────────────────────────────────────────


async def _stream_anthropic(
    config: ProviderConfig,
    prompt: str,
) -> AsyncGenerator[tuple[str, str], None]:
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=config.api_key)
    try:
        async with client.messages.stream(
            model=config.effective_model,
            max_tokens=MAX_TOKENS,
            system=ANTHROPIC_SYSTEM_PROMPT,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            searching = False
            async for event in stream:
                etype = getattr(event, "type", None)

                if etype == "content_block_start":
                    block = getattr(event, "content_block", None)
                    if block:
                        if (
                            getattr(block, "type", None) == "tool_use"
                            and getattr(block, "name", None) == "web_search"
                        ):
                            searching = True
                            yield ("searching", "")

                elif etype == "content_block_delta":
                    delta = getattr(event, "delta", None)
                    if delta and getattr(delta, "type", None) == "text_delta":
                        text = getattr(delta, "text", "")
                        if text:
                            yield ("text", text)

                elif etype == "content_block_stop":
                    if searching:
                        searching = False
                        yield ("search_done", "")

    except anthropic.RateLimitError:
        yield ("rate_limit", "")
    except anthropic.APIConnectionError as exc:
        yield ("error", f"Connection error: {exc}")
    except anthropic.APIStatusError as exc:
        yield ("error", f"API error {exc.status_code}: {exc.message}")
    except Exception as exc:  # noqa: BLE001
        yield ("error", str(exc))


# ─── Ollama / OpenAI-compatible backend ───────────────────────────────────────


async def _stream_ollama(
    config: ProviderConfig,
    prompt: str,
) -> AsyncGenerator[tuple[str, str], None]:
    from openai import AsyncOpenAI, APIConnectionError, RateLimitError, APIStatusError

    client = AsyncOpenAI(
        base_url=config.ollama_base_url,
        api_key=config.api_key or "ollama",  # Ollama ignores the key but SDK requires one
    )
    try:
        response = await client.chat.completions.create(
            model=config.effective_model,
            messages=[
                {"role": "system", "content": OLLAMA_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            stream=True,
            max_tokens=MAX_TOKENS,
        )
        async for chunk in response:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield ("text", delta.content)

    except RateLimitError:
        yield ("rate_limit", "")
    except APIConnectionError as exc:
        yield ("error", f"Cannot connect to Ollama at {config.ollama_base_url} — is it running? ({exc})")
    except APIStatusError as exc:
        yield ("error", f"API error {exc.status_code}: {exc.message}")
    except Exception as exc:  # noqa: BLE001
        yield ("error", str(exc))


# ─── Public interface ─────────────────────────────────────────────────────────


async def stream_stage(
    config: ProviderConfig,
    prompt: str,
) -> AsyncGenerator[tuple[str, str], None]:
    """
    Stream a single research stage for any provider.

    Yields (event_type, content) tuples:
      ('text',        token)    — text token to append to output
      ('searching',   '')       — Anthropic web search started
      ('search_done', '')       — web search block finished
      ('rate_limit',  '')       — rate-limit hit; caller should retry
      ('error',       message)  — unrecoverable error
    """
    if config.provider == "anthropic":
        async for event in _stream_anthropic(config, prompt):
            yield event
    else:
        async for event in _stream_ollama(config, prompt):
            yield event
