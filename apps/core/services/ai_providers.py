"""AI Provider abstractions for different AI services"""
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from django.conf import settings
from openai import OpenAI

logger = logging.getLogger('githubai')


class AIProviderError(Exception):
    """Base exception for AI provider errors"""
    pass


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int, base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = base_url
        self._client = None

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name"""
        pass

    @abstractmethod
    def get_client(self):
        """Get the client instance for this provider"""
        pass

    @abstractmethod
    def call_chat_completion(self, messages: list, model: Optional[str] = None,
                           temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        Call the chat completion API

        Returns:
            Dict containing:
                - content: The response content
                - tokens_used: Number of tokens used
                - model: Model used for the request
        """
        pass

    def validate_configuration(self) -> bool:
        """Validate that the provider is properly configured"""
        if not self.api_key:
            logger.error(f"API key not provided for {self.provider_name}")
            return False
        if not self.model:
            logger.error(f"Model not specified for {self.provider_name}")
            return False
        return True


class OpenAIProvider(AIProvider):
    """OpenAI API provider"""

    @property
    def provider_name(self) -> str:
        return "openai"

    def get_client(self):
        """Get OpenAI client instance"""
        if self._client is None:
            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            self._client = OpenAI(**client_kwargs)
        return self._client

    def call_chat_completion(self, messages: list, model: Optional[str] = None,
                           temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Call OpenAI chat completion API"""
        client = self.get_client()

        request_model = model or self.model
        request_temperature = temperature if temperature is not None else self.temperature
        request_max_tokens = max_tokens or self.max_tokens

        try:
            response = client.chat.completions.create(
                model=request_model,
                messages=messages,
                temperature=request_temperature,
                max_tokens=request_max_tokens
            )

            content = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None

            return {
                "content": content,
                "tokens_used": tokens_used,
                "model": request_model,
                "provider": self.provider_name
            }

        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise AIProviderError(f"OpenAI API error: {str(e)}")


class XAIProvider(AIProvider):
    """XAI (Grok) API provider"""

    @property
    def provider_name(self) -> str:
        return "xai"

    def get_client(self):
        """Get XAI client instance (using OpenAI-compatible client)"""
        if self._client is None:
            # XAI API is OpenAI-compatible
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://api.x.ai/v1"
            )
        return self._client

    def call_chat_completion(self, messages: list, model: Optional[str] = None,
                           temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Call XAI chat completion API"""
        client = self.get_client()

        request_model = model or self.model
        request_temperature = temperature if temperature is not None else self.temperature
        request_max_tokens = max_tokens or self.max_tokens

        try:
            response = client.chat.completions.create(
                model=request_model,
                messages=messages,
                temperature=request_temperature,
                max_tokens=request_max_tokens
            )

            content = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None

            return {
                "content": content,
                "tokens_used": tokens_used,
                "model": request_model,
                "provider": self.provider_name
            }

        except Exception as e:
            logger.error(f"XAI API call failed: {str(e)}")
            raise AIProviderError(f"XAI API error: {str(e)}")


class AIProviderFactory:
    """Factory for creating AI provider instances"""

    PROVIDERS = {
        "openai": OpenAIProvider,
        "xai": XAIProvider,
    }

    @classmethod
    def register_provider(cls, name: str, provider_class):
        """Register a new provider (useful for testing with MockAIProvider)"""
        cls.PROVIDERS[name] = provider_class
        logger.info(f"Registered AI provider: {name}")

    @classmethod
    def create_provider(cls, provider_name: Optional[str] = None,
                       api_key: Optional[str] = None,
                       model: Optional[str] = None,
                       temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None,
                       base_url: Optional[str] = None) -> AIProvider:
        """
        Create an AI provider instance based on configuration

        Args:
            provider_name: Optional provider name override
            api_key: Optional API key override
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            base_url: Optional base_url override

        Returns:
            AIProvider instance

        Raises:
            AIProviderError: If provider is not supported or misconfigured
        """
        provider_name = provider_name or settings.AI_PROVIDER

        if provider_name not in cls.PROVIDERS:
            raise AIProviderError(f"Unsupported AI provider: {provider_name}. Available: {list(cls.PROVIDERS.keys())}")

        provider_class = cls.PROVIDERS[provider_name]

        # Get provider-specific configuration from settings (if not overridden)
        if provider_name == "openai":
            api_key = api_key or settings.OPENAI_API_KEY
            model = model or settings.OPENAI_MODEL
            temperature = temperature if temperature is not None else settings.OPENAI_TEMPERATURE
            max_tokens = max_tokens or settings.OPENAI_MAX_TOKENS
            base_url = base_url or getattr(settings, 'OPENAI_BASE_URL', None)
        elif provider_name == "xai":
            api_key = api_key or settings.XAI_API_KEY
            model = model or settings.XAI_MODEL
            temperature = temperature if temperature is not None else settings.XAI_TEMPERATURE
            max_tokens = max_tokens or settings.XAI_MAX_TOKENS
            base_url = base_url or getattr(settings, 'XAI_BASE_URL', "https://api.x.ai/v1")
        elif provider_name == "mock":
            api_key = api_key or getattr(settings, 'MOCK_API_KEY', 'mock-test-key')
            model = model or getattr(settings, 'MOCK_MODEL', 'mock-gpt-4')
            temperature = temperature if temperature is not None else 0.7
            max_tokens = max_tokens or 1000
            base_url = base_url or getattr(settings, 'MOCK_BASE_URL', None)
        else:
            raise AIProviderError(f"Provider configuration not found for: {provider_name}")

        provider = provider_class(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            base_url=base_url
        )

        if not provider.validate_configuration():
            raise AIProviderError(f"Provider configuration validation failed for: {provider_name}")

        return provider

    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available providers"""
        return list(cls.PROVIDERS.keys())