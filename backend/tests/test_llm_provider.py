"""Tests for the Groq LLM provider."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.llm.provider import FailoverProvider, GroqProvider


@pytest.mark.asyncio
async def test_groq_provider_generate_json(caplog):
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content='{"hypotheses": []}')
            )
        ]
    )
    client = MagicMock()
    client.chat.completions.create.return_value = response

    caplog.set_level("INFO", logger="app.llm.provider")
    with patch("groq.Groq", return_value=client) as groq_client:
        provider = GroqProvider(api_key="test-key", model="openai/gpt-oss-120b")
        result = await provider.generate_json("Investigate this", "an object")

    assert result == {"hypotheses": []}
    groq_client.assert_called_once_with(api_key="test-key")
    client.chat.completions.create.assert_called_once()
    request = client.chat.completions.create.call_args.kwargs
    assert request["model"] == "openai/gpt-oss-120b"
    assert request["response_format"] == {"type": "json_object"}
    assert request["messages"][-1]["content"] == (
        "Investigate this\n\nRespond with valid JSON matching: an object"
    )
    assert "Groq API POST /openai/v1/chat/completions started" in caplog.text
    assert "Groq API response received" in caplog.text


@pytest.mark.asyncio
async def test_groq_provider_requires_api_key():
    provider = GroqProvider(api_key="")

    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        await provider.generate_json("prompt", "object")


@pytest.mark.asyncio
async def test_failover_provider_uses_gemini_after_groq_failure(caplog):
    groq_provider = MagicMock()
    groq_provider.generate_json = AsyncMock(side_effect=RuntimeError("Groq unavailable"))
    gemini_provider = MagicMock()
    gemini_provider.generate_json = AsyncMock(return_value={"hypotheses": []})

    caplog.set_level("WARNING", logger="app.llm.provider")
    provider = FailoverProvider(groq_provider, gemini_provider)
    result = await provider.generate_json("prompt", "object")

    assert result == {"hypotheses": []}
    groq_provider.generate_json.assert_awaited_once_with("prompt", "object")
    gemini_provider.generate_json.assert_awaited_once_with("prompt", "object")
    assert "trying Gemini fallback" in caplog.text
