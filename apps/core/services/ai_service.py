"""AI Services - vendor agnostic AI API interactions"""
import hashlib
import logging
import time
from django.conf import settings
from core.models import APILog, AIResponse
from core.services.ai_providers import AIProviderFactory, AIProviderError

logger = logging.getLogger('githubai')


class AIService:
    """Service for AI API interactions with caching"""

    def __init__(self, provider_name: str = None):
        """
        Initialize AI service with specified provider

        Args:
            provider_name: Optional provider name override (openai, xai)
        """
        self.provider_name = provider_name or settings.AI_PROVIDER
        self.provider = AIProviderFactory.create_provider(self.provider_name)

        # Legacy properties for backward compatibility
        self.model = self.provider.model
        self.temperature = self.provider.temperature
        self.max_tokens = self.provider.max_tokens

    def call_ai_chat(self, system_prompt, user_prompt,
                        model=None, temperature=None, max_tokens=None,
                        use_cache=True, provider_name=None):
        """
        Call AI Chat API with caching support.
        Vendor agnostic implementation supporting multiple AI providers

        Args:
            system_prompt: System prompt for the AI
            user_prompt: User prompt for the AI
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            use_cache: Whether to use caching
            provider_name: Optional provider override (openai, xai)
        """
        # Use different provider if specified
        if provider_name and provider_name != self.provider_name:
            temp_provider = AIProviderFactory.create_provider(provider_name)
            active_provider = temp_provider
        else:
            active_provider = self.provider

        # Use provider defaults or overrides
        request_model = model or active_provider.model
        request_temperature = temperature if temperature is not None else active_provider.temperature
        request_max_tokens = max_tokens or active_provider.max_tokens

        # Generate hash for caching (include provider info)
        prompt_hash = self._generate_prompt_hash(
            system_prompt, user_prompt, request_model,
            request_temperature, active_provider.provider_name
        )

        # Check cache if enabled
        if use_cache:
            cached_response = self._get_cached_response(prompt_hash)
            if cached_response:
                logger.info(f"Cache hit for prompt hash: {prompt_hash[:8]}")
                return cached_response

        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Log the request
        api_log = APILog.objects.create(
            api_type='ai',
            endpoint=f'/{active_provider.provider_name}/chat/completions',
            method='POST',
            request_data={
                'provider': active_provider.provider_name,
                'model': request_model,
                'messages': messages,
                'temperature': request_temperature,
                'max_tokens': request_max_tokens,
            },
            user_id=getattr(settings, 'USER_ID', 'unknown_user')
        )

        try:
            start_time = time.time()

            # Call provider API
            response_data = active_provider.call_chat_completion(
                messages=messages,
                model=request_model,
                temperature=request_temperature,
                max_tokens=request_max_tokens
            )

            duration_ms = int((time.time() - start_time) * 1000)
            content = response_data["content"]
            tokens_used = response_data.get("tokens_used")

            # Update API log
            api_log.status_code = 200
            api_log.duration_ms = duration_ms
            api_log.response_data = {
                'content': content[:500],  # Store truncated version
                'tokens_used': tokens_used,
                'provider': active_provider.provider_name,
                'model_used': response_data.get("model"),
            }
            api_log.save()

            # Cache the response
            if use_cache:
                self._cache_response(
                    prompt_hash, system_prompt, user_prompt,
                    content, request_model, request_temperature,
                    request_max_tokens, tokens_used, active_provider.provider_name
                )

            logger.info(f"AI API call successful. Provider: {active_provider.provider_name}, "
                       f"Tokens: {tokens_used}, Duration: {duration_ms}ms")
            return content

        except AIProviderError as e:
            # Update API log with provider error
            api_log.error_message = str(e)
            api_log.status_code = 500
            api_log.save()

            logger.error(f"AI Provider error ({active_provider.provider_name}): {str(e)}")
            raise

        except Exception as e:
            # Update API log with generic error
            api_log.error_message = str(e)
            api_log.status_code = 500
            api_log.save()

            logger.error(f"AI API error ({active_provider.provider_name}): {str(e)}")
            raise

    def _generate_prompt_hash(self, system_prompt, user_prompt, model, temperature, provider_name):
        """Generate hash for prompt caching including provider information"""
        content = f"{provider_name}|{model}|{temperature}|{system_prompt}|{user_prompt}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _get_cached_response(self, prompt_hash):
        """Retrieve cached response"""
        try:
            cached = AIResponse.objects.get(prompt_hash=prompt_hash)
            cached.increment_cache_hit()
            return cached.response_content
        except AIResponse.DoesNotExist:
            return None

    def _cache_response(self, prompt_hash, system_prompt, user_prompt,
                       content, model, temperature, max_tokens, tokens_used, provider_name):
        """Cache the AI response with provider information"""
        try:
            AIResponse.objects.create(
                prompt_hash=prompt_hash,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_content=content,
                model=model,
                provider=provider_name,
                temperature=temperature,
                max_tokens=max_tokens,
                tokens_used=tokens_used
            )
            logger.debug(f"Cached response ({provider_name}) with hash: {prompt_hash[:8]}")
        except Exception as e:
            logger.warning(f"Could not cache response ({provider_name}): {e}")

    @classmethod
    def get_available_providers(cls):
        """Get list of available AI providers"""
        return AIProviderFactory.get_available_providers()

    @classmethod
    def get_current_provider(cls):
        """Get the currently configured provider name"""
        return getattr(settings, 'AI_PROVIDER', 'openai')

    def switch_provider(self, provider_name: str):
        """
        Switch to a different provider

        Args:
            provider_name: Name of the provider to switch to
        """
        self.provider_name = provider_name
        self.provider = AIProviderFactory.create_provider(provider_name)
        self.model = self.provider.model
        self.temperature = self.provider.temperature
        self.max_tokens = self.provider.max_tokens

        logger.info(f"Switched AI provider to: {provider_name}")
