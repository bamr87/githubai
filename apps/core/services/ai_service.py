"""AI Services - vendor agnostic AI API interactions"""
import hashlib
import logging
import time
from typing import Optional, Dict, Any, List
from jinja2 import Template, TemplateError
from django.conf import settings
from django.utils import timezone
from core.models import APILog, AIResponse, AIProvider, AIModel
from core.services.ai_providers import AIProviderFactory, AIProviderError
from core.exceptions import (
    PromptTemplateNotFoundError,
    PromptRenderError,
    PromptValidationError
)

logger = logging.getLogger('githubai')


class AIService:
    """Service for AI API interactions with caching"""

    def __init__(self, provider_name: Optional[str] = None, ai_model_id: Optional[int] = None) -> None:
        """
        Initialize AI service with specified provider or model

        Args:
            provider_name: Optional provider name override (openai, xai) - legacy support
            ai_model_id: Optional AIModel ID to use specific model from database
        """
        # New way: Use database configuration
        if ai_model_id:
            try:
                self.ai_model = AIModel.objects.select_related('provider').get(
                    id=ai_model_id,
                    is_active=True
                )
                self.ai_provider = self.ai_model.provider
            except AIModel.DoesNotExist:
                raise ValueError(f"AIModel with id {ai_model_id} not found or inactive")
        elif provider_name:
            # Legacy support: get default model for provider
            try:
                self.ai_provider = AIProvider.objects.get(name=provider_name, is_active=True)
                self.ai_model = self.ai_provider.models.filter(is_active=True, is_default=True).first()
                if not self.ai_model:
                    # Fallback to any active model
                    self.ai_model = self.ai_provider.models.filter(is_active=True).first()
                if not self.ai_model:
                    raise ValueError(f"No active models found for provider {provider_name}")
            except AIProvider.DoesNotExist:
                # Fallback to legacy settings-based config
                logger.warning(f"Provider {provider_name} not in database, using legacy settings")
                self.ai_provider = None
                self.ai_model = None
                self._init_legacy_provider(provider_name)
                return
        else:
            # Default: Use settings or first available provider
            default_provider_name = getattr(settings, 'AI_PROVIDER', 'openai')
            try:
                self.ai_provider = AIProvider.objects.get(name=default_provider_name, is_active=True)
                self.ai_model = self.ai_provider.models.filter(is_active=True, is_default=True).first()
                if not self.ai_model:
                    self.ai_model = self.ai_provider.models.filter(is_active=True).first()
                if not self.ai_model:
                    raise ValueError(f"No active models found for default provider {default_provider_name}")
            except AIProvider.DoesNotExist:
                # Fallback to legacy
                logger.warning(f"No database configuration found, using legacy settings")
                self.ai_provider = None
                self.ai_model = None
                self._init_legacy_provider(default_provider_name)
                return

        # Initialize provider client using database configuration
        if self.ai_provider and self.ai_provider.has_api_key:
            self.provider_name = self.ai_provider.name
            self.provider = AIProviderFactory.create_provider(
                self.ai_provider.name,
                api_key=self.ai_provider.api_key,
                base_url=self.ai_provider.base_url,
                model=self.ai_model.name,
                temperature=self.ai_provider.default_temperature,
                max_tokens=self.ai_model.max_tokens
            )
        else:
            # Fallback if no API key in database
            logger.warning(f"No API key configured for {self.ai_provider.name}, using environment settings")
            self._init_legacy_provider(self.ai_provider.name)

        # Legacy properties for backward compatibility
        self.model = self.ai_model.name if self.ai_model else getattr(settings, 'AI_MODEL', 'gpt-4o-mini')
        self.temperature = self.ai_provider.default_temperature if self.ai_provider else 0.2
        self.max_tokens = self.ai_model.max_tokens if self.ai_model else 2500

    def _init_legacy_provider(self, provider_name: str) -> None:
        """Initialize using legacy settings-based configuration"""
        self.provider_name: str = provider_name
        self.provider = AIProviderFactory.create_provider(provider_name)
        self.model: str = self.provider.model
        self.temperature: float = self.provider.temperature
        self.max_tokens: int = self.provider.max_tokens

    def call_ai_chat(
        self,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_cache: bool = True,
        provider_name: Optional[str] = None,
        prompt_template_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Call AI Chat API with caching support.
        Vendor agnostic implementation supporting multiple AI providers

        Supports two modes:
        1. Direct prompt mode (legacy): Pass system_prompt and user_prompt directly
        2. Template mode: Pass prompt_template_id and context for Jinja2 rendering

        Args:
            system_prompt: System prompt for the AI (direct mode)
            user_prompt: User prompt for the AI (direct mode)
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            use_cache: Whether to use caching
            provider_name: Optional provider override (openai, xai)
            prompt_template_id: ID of PromptTemplate to use (template mode)
            context: Dict of variables for Jinja2 template rendering (template mode)

        Returns:
            str: AI response content

        Raises:
            PromptTemplateNotFoundError: If template not found
            PromptRenderError: If Jinja2 rendering fails
        """
        prompt_template = None
        rendered_system_prompt = system_prompt
        rendered_user_prompt = user_prompt

        # Template mode - load and render prompt template
        if prompt_template_id:
            from core.models import PromptTemplate, PromptExecution

            try:
                prompt_template = PromptTemplate.objects.get(
                    id=prompt_template_id,
                    is_active=True
                )
            except PromptTemplate.DoesNotExist:
                raise PromptTemplateNotFoundError(
                    f"PromptTemplate with id {prompt_template_id} not found or inactive"
                )

            # Render templates with Jinja2
            context = context or {}
            try:
                system_template = Template(prompt_template.system_prompt)
                rendered_system_prompt = system_template.render(**context)

                user_template = Template(prompt_template.user_prompt_template)
                rendered_user_prompt = user_template.render(**context)
            except TemplateError as e:
                raise PromptRenderError(f"Failed to render prompt template: {str(e)}")

            # Use template's model configuration if not overridden
            # Priority: explicit param > template's ai_model > template's legacy fields > service defaults
            if prompt_template.ai_model and not model:
                # Use database-configured model
                template_ai_model = prompt_template.ai_model
                model = model or template_ai_model.name
                temperature = temperature if temperature is not None else prompt_template.temperature
                max_tokens = max_tokens or template_ai_model.max_tokens

                # Use model's provider if not explicitly overridden
                if not provider_name:
                    provider_name = template_ai_model.provider.name
            else:
                # Fallback to legacy fields
                model = model or prompt_template.model
                temperature = temperature if temperature is not None else prompt_template.temperature
                max_tokens = max_tokens or prompt_template.max_tokens

                # Use template's provider preference if specified (legacy)
                if prompt_template.provider != 'auto' and not provider_name:
                    provider_name = prompt_template.provider

            # Increment usage counter
            prompt_template.increment_usage()

        # Validate we have prompts (either direct or rendered)
        if not rendered_system_prompt or not rendered_user_prompt:
            raise ValueError("Must provide either system_prompt/user_prompt or prompt_template_id with context")

        # Determine which AI model to use (database or legacy)
        active_ai_model = None
        if provider_name:
            # Try to get model from database
            try:
                active_provider_obj = AIProvider.objects.get(name=provider_name, is_active=True)
                if model:
                    # Specific model requested
                    active_ai_model = active_provider_obj.models.filter(name=model, is_active=True).first()
                else:
                    # Use default model for provider
                    active_ai_model = active_provider_obj.models.filter(is_default=True, is_active=True).first()
                    if not active_ai_model:
                        active_ai_model = active_provider_obj.models.filter(is_active=True).first()
            except AIProvider.DoesNotExist:
                pass
        elif model and self.ai_model:
            # Check if model name matches current AI model or try to find it
            if self.ai_model.name != model:
                active_ai_model = AIModel.objects.filter(name=model, is_active=True).first()
            else:
                active_ai_model = self.ai_model
        else:
            # Use current service's model
            active_ai_model = self.ai_model if hasattr(self, 'ai_model') else None

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
            rendered_system_prompt, rendered_user_prompt, request_model,
            request_temperature, active_provider.provider_name
        )

        # Check cache if enabled
        cache_hit = False
        if use_cache:
            cached_response = self._get_cached_response(prompt_hash)
            if cached_response:
                logger.info(f"Cache hit for prompt hash: {prompt_hash[:8]}")
                cache_hit = True

                # Log execution if using template
                if prompt_template:
                    self._log_prompt_execution(
                        prompt_template=prompt_template,
                        input_variables=context,
                        rendered_system_prompt=rendered_system_prompt,
                        rendered_user_prompt=rendered_user_prompt,
                        output_content=cached_response,
                        provider_used=active_provider.provider_name,
                        model_used=request_model,
                        temperature_used=request_temperature,
                        tokens_used=None,
                        duration_ms=0,
                        cache_hit=True,
                        success=True,
                        ai_model=active_ai_model
                    )

                return cached_response

        # Prepare messages
        messages = [
            {"role": "system", "content": rendered_system_prompt},
            {"role": "user", "content": rendered_user_prompt},
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
                'template_id': prompt_template_id,
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
                    prompt_hash, rendered_system_prompt, rendered_user_prompt,
                    content, request_model, request_temperature,
                    request_max_tokens, tokens_used, active_provider.provider_name,
                    ai_model=active_ai_model
                )

            # Log execution if using template
            if prompt_template:
                self._log_prompt_execution(
                    prompt_template=prompt_template,
                    input_variables=context,
                    rendered_system_prompt=rendered_system_prompt,
                    rendered_user_prompt=rendered_user_prompt,
                    output_content=content,
                    provider_used=active_provider.provider_name,
                    model_used=response_data.get("model", request_model),
                    temperature_used=request_temperature,
                    tokens_used=tokens_used,
                    duration_ms=duration_ms,
                    cache_hit=False,
                    success=True,
                    ai_model=active_ai_model
                )

            logger.info(f"AI API call successful. Provider: {active_provider.provider_name}, "
                       f"Tokens: {tokens_used}, Duration: {duration_ms}ms")
            return content

        except AIProviderError as e:
            # Update API log with provider error
            api_log.error_message = str(e)
            api_log.status_code = 500
            api_log.save()

            # Log failed execution if using template
            if prompt_template:
                self._log_prompt_execution(
                    prompt_template=prompt_template,
                    input_variables=context,
                    rendered_system_prompt=rendered_system_prompt,
                    rendered_user_prompt=rendered_user_prompt,
                    output_content='',
                    provider_used=active_provider.provider_name,
                    model_used=request_model,
                    temperature_used=request_temperature,
                    tokens_used=None,
                    duration_ms=duration_ms,
                    cache_hit=False,
                    success=False,
                    error_message=str(e),
                    ai_model=active_ai_model
                )

            logger.error(f"AI Provider error ({active_provider.provider_name}): {str(e)}")
            raise

        except Exception as e:
            # Update API log with generic error
            api_log.error_message = str(e)
            api_log.status_code = 500
            api_log.save()

            # Log failed execution if using template
            if prompt_template:
                self._log_prompt_execution(
                    prompt_template=prompt_template,
                    input_variables=context,
                    rendered_system_prompt=rendered_system_prompt,
                    rendered_user_prompt=rendered_user_prompt,
                    output_content="",
                    provider_used=active_provider.provider_name,
                    model_used=request_model,
                    temperature_used=request_temperature,
                    tokens_used=None,
                    duration_ms=None,
                    cache_hit=False,
                    success=False,
                    error_message=str(e)
                )

            logger.error(f"AI API error ({active_provider.provider_name}): {str(e)}")
            raise

    def _generate_prompt_hash(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float,
        provider_name: str
    ) -> str:
        """Generate hash for prompt caching including provider information"""
        content = f"{provider_name}|{model}|{temperature}|{system_prompt}|{user_prompt}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _get_cached_response(self, prompt_hash: str) -> Optional[str]:
        """Retrieve cached response"""
        try:
            cached = AIResponse.objects.get(prompt_hash=prompt_hash)
            cached.increment_cache_hit()
            return cached.response_content
        except AIResponse.DoesNotExist:
            return None

    def _cache_response(
        self,
        prompt_hash: str,
        system_prompt: str,
        user_prompt: str,
        content: str,
        model: str,
        temperature: float,
        max_tokens: int,
        tokens_used: Optional[int],
        provider_name: str,
        ai_model: Optional[AIModel] = None
    ) -> None:
        """Cache the AI response with provider information"""
        try:
            AIResponse.objects.create(
                prompt_hash=prompt_hash,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_content=content,
                ai_model=ai_model,  # Store reference to AIModel
                model=model,  # Keep legacy field
                provider=provider_name,  # Keep legacy field
                temperature=temperature,
                max_tokens=max_tokens,
                tokens_used=tokens_used
            )
            logger.debug(f"Cached response ({provider_name}) with hash: {prompt_hash[:8]}")
        except Exception as e:
            logger.warning(f"Could not cache response ({provider_name}): {e}")

    def _log_prompt_execution(
        self,
        prompt_template,
        input_variables: Dict[str, Any],
        rendered_system_prompt: str,
        rendered_user_prompt: str,
        output_content: str,
        provider_used: str,
        model_used: str,
        temperature_used: float,
        tokens_used: Optional[int],
        duration_ms: Optional[int],
        cache_hit: bool,
        success: bool,
        error_message: Optional[str] = None,
        ai_model: Optional[AIModel] = None
    ) -> None:
        """Log prompt template execution for analytics"""
        from core.models import PromptExecution

        try:
            PromptExecution.objects.create(
                prompt=prompt_template,
                ai_model=ai_model,  # Store reference to AIModel
                input_variables=input_variables,
                rendered_system_prompt=rendered_system_prompt,
                rendered_user_prompt=rendered_user_prompt,
                output_content=output_content,
                provider_used=provider_used,  # Keep legacy field
                model_used=model_used,  # Keep legacy field
                temperature_used=temperature_used,
                tokens_used=tokens_used,
                duration_ms=duration_ms,
                cache_hit=cache_hit,
                success=success,
                error_message=error_message
            )
            logger.debug(f"Logged prompt execution for template: {prompt_template.name}")
        except Exception as e:
            logger.warning(f"Could not log prompt execution: {e}")

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available AI providers"""
        return AIProviderFactory.get_available_providers()

    @classmethod
    def get_current_provider(cls) -> str:
        """Get the currently configured provider name"""
        return getattr(settings, 'AI_PROVIDER', 'openai')

    def switch_provider(self, provider_name: str) -> None:
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
