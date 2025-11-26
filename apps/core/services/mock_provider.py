"""Mock AI Provider for deterministic testing without API costs"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from django.conf import settings

logger = logging.getLogger("githubai")


class MockAIProvider:
    """
    Mock AI provider that returns canned responses from a fixture file.

    This provider allows deterministic testing of AI-generated content
    without making real API calls or incurring costs.

    Responses are loaded from a dated fixture file (e.g., test_ai_responses_2025-11-25.json)
    and returned based on:
    1. Exact prompt match (if available)
    2. Category-based fallback (e.g., "code_quality", "chat", "auto_issue")
    3. Default fallback response

    Usage:
        # In .env.test:
        AI_PROVIDER=mock
        MOCK_API_KEY=mock-test-key-2025-11-25
        MOCK_MODEL=mock-gpt-4
        MOCK_AI_RESPONSES_FIXTURE=apps/core/fixtures/test_ai_responses_2025-11-25.json
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float,
        max_tokens: int,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = base_url
        self._client = None
        self._responses = None
        self._call_count = 0

        # Load canned responses from fixture
        self._load_responses()

    @property
    def provider_name(self) -> str:
        return "mock"

    def get_client(self):
        """Return self as the 'client' (no real client needed)"""
        return self

    def _load_responses(self):
        """Load canned responses from fixture file"""
        fixture_path = getattr(
            settings,
            "MOCK_AI_RESPONSES_FIXTURE",
            "apps/core/fixtures/test_ai_responses_2025-11-25.json",
        )

        try:
            # Handle both absolute and relative paths
            if not Path(fixture_path).is_absolute():
                fixture_path = settings.BASE_DIR / fixture_path

            with open(fixture_path, "r") as f:
                self._responses = json.load(f)

            logger.info(
                f"MockAIProvider loaded {len(self._responses.get('responses', []))} "
                f"canned responses from {fixture_path}"
            )

        except FileNotFoundError:
            logger.warning(
                f"Mock AI responses fixture not found at {fixture_path}. "
                "Using default fallback responses only."
            )
            self._responses = {"responses": [], "fallbacks": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse mock AI responses fixture: {e}")
            self._responses = {"responses": [], "fallbacks": {}}

    def _find_response(self, messages: list) -> Dict[str, Any]:
        """
        Find appropriate canned response for the given messages.

        Strategy:
        1. Try exact prompt match (last user message)
        2. Try category-based match (from message metadata)
        3. Use default fallback
        """
        if not self._responses:
            return self._get_default_response()

        # Extract last user message as the prompt
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return self._get_default_response()

        last_user_message = user_messages[-1].get("content", "")

        # Try exact match first
        for response_entry in self._responses.get("responses", []):
            if response_entry.get("prompt") == last_user_message:
                logger.debug(
                    f"MockAIProvider: Found exact match for prompt (length: {len(last_user_message)})"
                )
                return {
                    "content": response_entry.get("response", ""),
                    "tokens_used": response_entry.get("tokens_used", 100),
                    "model": self.model,
                    "provider": self.provider_name,
                }

        # Try category-based match
        # Check if prompt contains category keywords
        prompt_lower = last_user_message.lower()
        fallbacks = self._responses.get("fallbacks", {})

        for category, keywords in [
            ("code_quality", ["code quality", "refactor", "bug", "technical debt"]),
            ("auto_issue", ["issue", "github", "repository"]),
            ("chat", ["hello", "help", "what", "how", "explain"]),
            ("prompt_template", ["template", "prompt", "instruction"]),
        ]:
            if any(keyword in prompt_lower for keyword in keywords):
                if category in fallbacks:
                    logger.debug(
                        f"MockAIProvider: Using category fallback for '{category}'"
                    )
                    return {
                        "content": fallbacks[category],
                        "tokens_used": 100,
                        "model": self.model,
                        "provider": self.provider_name,
                    }

        # Use default fallback
        logger.debug("MockAIProvider: Using default fallback response")
        return self._get_default_response()

    def _get_default_response(self) -> Dict[str, Any]:
        """Return default fallback response"""
        default_content = self._responses.get("fallbacks", {}).get(
            "default",
            "This is a mock AI response for testing purposes. "
            "The actual response would be generated by a real AI model.",
        )

        return {
            "content": default_content,
            "tokens_used": 50,
            "model": self.model,
            "provider": self.provider_name,
        }

    def call_chat_completion(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Mock chat completion - returns canned response without API call.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Ignored (uses configured mock model)
            temperature: Ignored (no randomness in mock)
            max_tokens: Ignored (canned responses are pre-generated)

        Returns:
            Dict with keys: content, tokens_used, model, provider
        """
        self._call_count += 1

        logger.info(
            f"MockAIProvider call #{self._call_count}: "
            f"{len(messages)} messages, model={model or self.model}"
        )

        # Log prompt for debugging
        user_messages = [m for m in messages if m.get("role") == "user"]
        if user_messages:
            prompt_preview = user_messages[-1].get("content", "")[:100]
            logger.debug(f"MockAIProvider prompt preview: {prompt_preview}...")

        # Find and return appropriate response
        response = self._find_response(messages)

        logger.info(
            f"MockAIProvider returning response: {len(response['content'])} chars, "
            f"{response['tokens_used']} tokens"
        )

        return response

    def validate_configuration(self) -> bool:
        """Validate mock provider configuration"""
        if not self.api_key:
            logger.error("Mock API key not provided")
            return False
        if not self.model:
            logger.error("Mock model not specified")
            return False

        # Check if responses loaded successfully
        if self._responses is None:
            logger.warning(
                "Mock AI responses not loaded - will use default fallback only"
            )

        return True

    def get_call_count(self) -> int:
        """Return number of mock API calls made (useful for testing)"""
        return self._call_count

    def reset_call_count(self):
        """Reset call counter (useful for testing)"""
        self._call_count = 0
