import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

from .services import get_ai_response
from .models import AILogs

@override_settings(
    OPENROUTER_API_KEY="test_api_key",
    OPENROUTER_MODEL="test_model",
)
class AILogicTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
    
    @patch("api.services.client.chat.completions.create", new_callable=AsyncMock)
    async def test_get_ai_response_success(self, mock_create):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Mocked AI response"))]
        mock_create.return_value = mock_response

        response = await get_ai_response("Test prompt", self.user)

        self.assertEqual(response, "Mocked AI response")

        self.assertEqual(await sync_to_async(AILogs.objects.count)(), 1)
        log = await sync_to_async(AILogs.objects.first)()
        self.assertEqual(log.prompt, "Test prompt")
        self.assertEqual(log.response, "Mocked AI response")

        self.assertEqual(await sync_to_async(lambda: log.user)(), self.user)
        self.assertEqual(log.model_name, "test_model")
        
    @patch("api.services.client.chat.completions.create", new_callable=AsyncMock)
    async def test_get_ai_response_api_error(self, mock_create):
        mock_create.side_effect = Exception("API connection error")

        response = await get_ai_response("Test prompt with error")

    
        self.assertIn("An error occurred: API connection error", response)
        
        self.assertEqual(await sync_to_async(AILogs.objects.count)(), 1)
        log = await sync_to_async(AILogs.objects.first)()
        self.assertIn("API connection error", log.response)
        self.assertIsNone(await sync_to_async(lambda: log.user)())
        self.assertEqual(log.model_name, "test_model")

    async def test_get_ai_response_missing_api_key(self):
        with override_settings(OPENROUTER_API_KEY=""):
            response = await get_ai_response("Test prompt")
            self.assertIn("OPENROUTER_API_KEY is not set", response)
            self.assertEqual(await sync_to_async(AILogs.objects.count)(), 0)