"""
LLM Client
Integration with Groq API (cloud) and Ollama (local) LLM providers.
"""

from typing import Optional, AsyncGenerator
from abc import ABC, abstractmethod
import httpx
import json

from app.config import settings
from app.logger import logger


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @property
    @abstractmethod
    def model(self) -> str:
        """Get the model name."""
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the LLM."""
        pass


class GroqClient(BaseLLMClient):
    """Client for interacting with Groq API (fast cloud inference)."""

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self._model = settings.GROQ_MODEL
        self.base_url = "https://api.groq.com/openai/v1"
        self.timeout = httpx.Timeout(60.0, connect=10.0)
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set in configuration")
    
    @property
    def model(self) -> str:
        return self._model
    
    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """Generate a response from Groq API."""
        if temperature is None:
            temperature = settings.LLM_TEMPERATURE
        if max_tokens is None:
            max_tokens = settings.LLM_MAX_TOKENS

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

        except httpx.TimeoutException:
            logger.error("Groq API request timed out")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"Groq API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Groq API generation error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from Groq API.
        
        Bug Fix #9: Added logging for JSON decode errors that previously failed silently.
        Now tracks malformed chunks for debugging while continuing stream.
        """
        if temperature is None:
            temperature = settings.LLM_TEMPERATURE
        if max_tokens is None:
            max_tokens = settings.LLM_MAX_TOKENS

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if delta := data.get("choices", [{}])[0].get("delta", {}).get("content"):
                                    yield delta
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse JSON from stream: {data_str[:100]}")
                                continue

        except Exception as e:
            logger.error(f"Groq API streaming error: {e}")
            raise


class OllamaClient(BaseLLMClient):
    """Client for interacting with Ollama API (local inference)."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self._model = settings.LLM_MODEL
        self.timeout = httpx.Timeout(120.0, connect=10.0)
    
    @property
    def model(self) -> str:
        return self._model

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """Generate a response from Ollama."""
        if temperature is None:
            temperature = settings.LLM_TEMPERATURE
        if max_tokens is None:
            max_tokens = settings.LLM_MAX_TOKENS

        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")

        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            raise
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from Ollama."""
        if temperature is None:
            temperature = settings.LLM_TEMPERATURE
        if max_tokens is None:
            max_tokens = settings.LLM_MAX_TOKENS

        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            if chunk := data.get("response"):
                                yield chunk
                            if data.get("done"):
                                break

        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise


# Global client instance
_llm_client: Optional[BaseLLMClient] = None


def get_llm_client() -> BaseLLMClient:
    """Get or create the LLM client instance based on configuration."""
    global _llm_client

    if _llm_client is None:
        provider = settings.LLM_PROVIDER.lower()
        
        if provider == "groq":
            logger.info(f"Initializing Groq client with model: {settings.GROQ_MODEL}")
            _llm_client = GroqClient()
        elif provider == "ollama":
            logger.info(f"Initializing Ollama client with model: {settings.LLM_MODEL}")
            _llm_client = OllamaClient()
        else:
            logger.warning(f"Unknown LLM provider '{provider}', defaulting to Groq")
            _llm_client = GroqClient()

    return _llm_client


async def check_llm_health() -> bool:
    """Check if the LLM service is available."""
    provider = settings.LLM_PROVIDER.lower()
    
    try:
        if provider == "groq":
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                response = await client.get(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                )
                return response.status_code == 200
        else:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                return response.status_code == 200
    except Exception as e:
        logger.warning(f"LLM health check failed: {e}")
        return False


async def list_available_models() -> list:
    """List available models from the configured provider."""
    provider = settings.LLM_PROVIDER.lower()
    
    try:
        if provider == "groq":
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                response = await client.get(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                )
                response.raise_for_status()
                data = response.json()
                return [model["id"] for model in data.get("data", [])]
        else:
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [model["name"] for model in data.get("models", [])]

    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return []
