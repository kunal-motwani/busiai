"""LLM Provider abstraction supporting Groq, Gemini, and deterministic reasoning."""
import asyncio
import json
import logging
import time
from typing import Any, Dict, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider:
    """Abstract interface for LLM reasoning."""

    async def generate_json(self, prompt: str, schema_description: str) -> Dict[str, Any]:
        """Generate structured JSON reasoning."""
        raise NotImplementedError


class GroqProvider(LLMProvider):
    """Groq chat-completions provider."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = settings.GROQ_API_KEY if api_key is None else api_key
        self.model_name = settings.GROQ_MODEL if model is None else model

    async def generate_json(self, prompt: str, schema_description: str) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured.")

        from groq import Groq

        client = Groq(api_key=self.api_key)
        started_at = time.perf_counter()
        logger.info(
            "Groq API POST /openai/v1/chat/completions started (model=%s)",
            self.model_name,
        )
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "Return only valid JSON. Do not include markdown fences.",
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nRespond with valid JSON matching: {schema_description}",
                    },
                ],
                response_format={"type": "json_object"},
            )
        except Exception:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            logger.exception(
                "Groq API POST /openai/v1/chat/completions failed (model=%s, elapsed_ms=%.0f)",
                self.model_name,
                elapsed_ms,
            )
            raise

        text = (response.choices[0].message.content or "").strip()
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "Groq API response received (model=%s, elapsed_ms=%.0f, response_chars=%d)",
            self.model_name,
            elapsed_ms,
            len(text),
        )
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())


class GeminiProvider(LLMProvider):
    """Google Gemini provider used when Groq is unavailable."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = settings.GEMINI_API_KEY if api_key is None else api_key
        self.model_name = settings.GEMINI_MODEL if model is None else model

    async def generate_json(self, prompt: str, schema_description: str) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)
        started_at = time.perf_counter()
        logger.info("Gemini API request started (model=%s)", self.model_name)
        try:
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=self.model_name,
                contents=f"{prompt}\n\nRespond with valid JSON matching: {schema_description}",
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                ),
            )
        except Exception:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            logger.exception(
                "Gemini API request failed (model=%s, elapsed_ms=%.0f)",
                self.model_name,
                elapsed_ms,
            )
            raise

        text = (response.text or "").strip()
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "Gemini API response received (model=%s, elapsed_ms=%.0f, response_chars=%d)",
            self.model_name,
            elapsed_ms,
            len(text),
        )
        return json.loads(text)


class FailoverProvider(LLMProvider):
    """Try the primary provider first, then use the configured fallback."""

    def __init__(self, primary: LLMProvider, fallback: LLMProvider):
        self.primary = primary
        self.fallback = fallback

    async def generate_json(self, prompt: str, schema_description: str) -> Dict[str, Any]:
        try:
            return await self.primary.generate_json(prompt, schema_description)
        except Exception as primary_error:
            logger.warning(
                "Primary Groq provider failed; trying Gemini fallback: %s",
                primary_error,
            )
            try:
                return await self.fallback.generate_json(prompt, schema_description)
            except Exception:
                logger.exception("Gemini fallback provider failed")
                raise primary_error


class DeterministicReasoner(LLMProvider):
    """Rule-based, heuristic intelligence engine for offline execution and fast testing."""

    async def generate_json(self, prompt: str, schema_description: str) -> Dict[str, Any]:
        # Return fallback structured response
        return {}


def get_llm_provider() -> LLMProvider:
    """Factory to instantiate configured provider."""
    # Groq is the primary provider whenever its key is configured. This also
    # prevents a stale LLM_PROVIDER environment variable from bypassing Groq.
    if settings.GROQ_API_KEY:
        groq_provider = GroqProvider()
        if settings.GEMINI_API_KEY:
            gemini_provider = GeminiProvider()
            logger.info(
                "Groq LLM provider selected with Gemini failover (groq_model=%s, gemini_model=%s)",
                groq_provider.model_name,
                gemini_provider.model_name,
            )
            return FailoverProvider(groq_provider, gemini_provider)
        logger.info("Groq LLM provider selected (model=%s)", groq_provider.model_name)
        return groq_provider

    if settings.GEMINI_API_KEY:
        provider = GeminiProvider()
        logger.warning(
            "Groq LLM provider unavailable; using Gemini fallback (model=%s)",
            provider.model_name,
        )
        return provider

    logger.warning("Groq and Gemini LLM providers unavailable; using deterministic fallback")
    return DeterministicReasoner()
