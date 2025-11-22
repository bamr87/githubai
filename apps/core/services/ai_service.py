"""AI Services - vendor agnostic AI API interactions"""
import hashlib
import logging
from django.conf import settings
from openai import OpenAI
from core.models import APILog, AIResponse

logger = logging.getLogger('githubai')


class AIService:
    """Service for AI API interactions with caching"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.AI_API_KEY)
        self.model = settings.AI_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS

    def call_ai_chat(self, system_prompt, user_prompt,
                        model=None, temperature=None, max_tokens=None,
                        use_cache=True):
        """
        Call AI Chat API with caching support.
        Vendor agnostic implementation supporting multiple AI providers
        """
        model = model or self.model
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens or self.max_tokens

        # Generate hash for caching
        prompt_hash = self._generate_prompt_hash(system_prompt, user_prompt, model, temperature)

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
            endpoint=f'/chat/completions',
            method='POST',
            request_data={
                'model': model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
            },
            user_id=getattr(settings, 'USER_ID', 'unknown_user')
        )

        try:
            import time
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            duration_ms = int((time.time() - start_time) * 1000)
            content = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None

            # Update API log
            api_log.status_code = 200
            api_log.duration_ms = duration_ms
            api_log.response_data = {
                'content': content[:500],  # Store truncated version
                'tokens_used': tokens_used,
            }
            api_log.save()

            # Cache the response
            if use_cache:
                self._cache_response(
                    prompt_hash, system_prompt, user_prompt,
                    content, model, temperature, max_tokens, tokens_used
                )

            logger.info(f"AI API call successful. Tokens: {tokens_used}, Duration: {duration_ms}ms")
            return content

        except Exception as e:
            # Update API log with error
            api_log.error_message = str(e)
            api_log.status_code = 500
            api_log.save()

            logger.error(f"AI API error: {str(e)}")
            raise

    def _generate_prompt_hash(self, system_prompt, user_prompt, model, temperature):
        """Generate hash for prompt caching"""
        content = f"{model}|{temperature}|{system_prompt}|{user_prompt}"
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
                       content, model, temperature, max_tokens, tokens_used):
        """Cache the AI response"""
        try:
            AIResponse.objects.create(
                prompt_hash=prompt_hash,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_content=content,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tokens_used=tokens_used
            )
            logger.debug(f"Cached response with hash: {prompt_hash[:8]}")
        except Exception as e:
            logger.warning(f"Could not cache response: {e}")
