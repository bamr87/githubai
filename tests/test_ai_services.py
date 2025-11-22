"""Tests for AI services."""

from unittest.mock import Mock, patch

import pytest
from core.models import AIResponse
from core.services import AIService
from django.test import TestCase


@pytest.mark.django_db
class TestOpenAIService:
    """Test cases for OpenAIService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = OpenAIService()

    def test_service_initialization(self):
        """Test OpenAIService can be instantiated."""
        assert self.service is not None

    def test_generate_prompt_hash(self):
        """Test generating hash for prompt."""
        system_prompt = "System prompt"
        user_prompt = "User prompt"
        model = "gpt-4o-mini"
        temperature = 0.2

        hash1 = self.service._generate_prompt_hash(
            system_prompt, user_prompt, model, temperature
        )
        hash2 = self.service._generate_prompt_hash(
            system_prompt, user_prompt, model, temperature
        )

        # Same prompt should generate same hash
        assert hash1 == hash2
        assert len(hash1) > 0

    def test_different_prompts_different_hashes(self):
        """Test different prompts generate different hashes."""
        system_prompt = "System prompt"
        user_prompt1 = "User prompt 1"
        user_prompt2 = "User prompt 2"
        model = "gpt-4o-mini"
        temperature = 0.2

        hash1 = self.service._generate_prompt_hash(
            system_prompt, user_prompt1, model, temperature
        )
        hash2 = self.service._generate_prompt_hash(
            system_prompt, user_prompt2, model, temperature
        )

        assert hash1 != hash2

    @pytest.mark.django_db
    def test_cache_response(self):
        """Test caching AI response."""
        system_prompt = "System prompt"
        user_prompt = "User prompt"
        response = "Test response"
        prompt_hash = self.service._generate_prompt_hash(
            system_prompt, user_prompt, "gpt-4o-mini", 0.2
        )

        cached = AIResponse.objects.create(
            prompt_hash=prompt_hash,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_content=response,
            model="gpt-4o-mini",
            tokens_used=100,
        )

        assert cached.id is not None
        assert cached.user_prompt == user_prompt
        assert cached.response_content == response

    @pytest.mark.django_db
    def test_retrieve_cached_response(self):
        """Test retrieving cached response."""
        system_prompt = "System prompt"
        user_prompt = "Cached test prompt"
        response = "Cached response"
        prompt_hash = self.service._generate_prompt_hash(
            system_prompt, user_prompt, "gpt-4o-mini", 0.2
        )

        # Cache the response
        AIResponse.objects.create(
            prompt_hash=prompt_hash,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_content=response,
            model="gpt-4o-mini",
            tokens_used=50,
        )

        # Try to retrieve it
        cached = AIResponse.objects.filter(prompt_hash=prompt_hash).first()

        assert cached is not None
        assert cached.response_content == response
        assert cached.tokens_used == 50

    @pytest.mark.django_db
    def test_cache_hit_count(self):
        """Test cache hit counting."""
        system_prompt = "System prompt"
        user_prompt = "Test prompt for hit count"
        prompt_hash = self.service._generate_prompt_hash(
            system_prompt, user_prompt, "gpt-4o-mini", 0.2
        )

        cached = AIResponse.objects.create(
            prompt_hash=prompt_hash,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_content="Response",
            model="gpt-4o-mini",
            tokens_used=100,
            cache_hit_count=0,
        )

        # Simulate cache hits using increment method
        cached.increment_cache_hit()

        updated = AIResponse.objects.get(id=cached.id)
        assert updated.cache_hit_count == 1

    @patch("core.services.openai_service.OpenAI")
    def test_call_openai_chat_no_cache(self, mock_openai_class):
        """Test getting chat completion without cache."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="AI generated response"))]
        mock_response.usage = Mock(total_tokens=150)
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        service = OpenAIService()
        result = service.call_openai_chat(
            "System prompt", "User prompt", use_cache=False
        )

        assert result is not None
        assert "AI generated response" in result

    @pytest.mark.django_db
    @patch("core.services.openai_service.OpenAI")
    def test_call_openai_chat_with_cache(self, mock_openai_class):
        """Test getting chat completion with caching."""
        system_prompt = "System prompt"
        user_prompt = "Cacheable prompt"
        prompt_hash = self.service._generate_prompt_hash(
            system_prompt, user_prompt, "gpt-4o-mini", 0.2
        )

        # Pre-cache a response
        AIResponse.objects.create(
            prompt_hash=prompt_hash,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_content="Cached AI response",
            model="gpt-4o-mini",
            tokens_used=100,
        )

        service = OpenAIService()
        result = service.call_openai_chat(system_prompt, user_prompt, use_cache=True)

        # Should return cached response without calling OpenAI
        assert result is not None
        assert result == "Cached AI response"
        mock_openai_class.assert_called()  # Client is created but chat.completions.create should not be called

    @pytest.mark.django_db
    def test_ai_response_model_str(self):
        """Test AIResponse model string representation."""
        response = AIResponse.objects.create(
            prompt_hash="abc123",
            system_prompt="System",
            user_prompt="Test",
            response_content="Response",
            model="gpt-4o-mini",
            tokens_used=50,
        )

        assert "gpt-4o-mini" in str(response)
        assert "abc123" in str(response)

    @pytest.mark.django_db
    def test_token_usage_tracking(self):
        """Test tracking token usage."""
        # Create multiple responses with different token usage
        AIResponse.objects.create(
            prompt_hash="hash1",
            system_prompt="System",
            user_prompt="Prompt 1",
            response_content="Response 1",
            model="gpt-4o-mini",
            tokens_used=100,
        )
        AIResponse.objects.create(
            prompt_hash="hash2",
            system_prompt="System",
            user_prompt="Prompt 2",
            response_content="Response 2",
            model="gpt-4o-mini",
            tokens_used=200,
        )

        total_tokens = sum(
            r.tokens_used for r in AIResponse.objects.all() if r.tokens_used
        )
        assert total_tokens == 300

    @pytest.mark.django_db
    def test_cache_statistics(self):
        """Test calculating cache statistics."""
        # Create responses with various cache hits
        AIResponse.objects.create(
            prompt_hash="hash1",
            system_prompt="System",
            user_prompt="P1",
            response_content="R1",
            model="gpt-4o-mini",
            tokens_used=100,
            cache_hit_count=5,
        )
        AIResponse.objects.create(
            prompt_hash="hash2",
            system_prompt="System",
            user_prompt="P2",
            response_content="R2",
            model="gpt-4o-mini",
            tokens_used=100,
            cache_hit_count=10,
        )

        total_hits = sum(r.cache_hit_count for r in AIResponse.objects.all())
        assert total_hits == 15

        # Calculate cache hit rate
        total_requests = AIResponse.objects.count() + total_hits
        cache_rate = total_hits / total_requests if total_requests > 0 else 0
        assert cache_rate > 0


class TestOpenAIServiceIntegration(TestCase):
    """Integration tests for OpenAI service."""

    @pytest.mark.skipif(
        True,  # Skip by default, use --run-integration to run
        reason="Integration tests require --run-integration flag",
    )
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_real_api_call(self):
        """Test real API call (requires valid API key)."""
        # This test would make a real API call
        # Only run when explicitly testing with real credentials
        pass
        pass
        pass
