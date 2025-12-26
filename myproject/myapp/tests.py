from django.test import TestCase, Client
from django.urls import reverse
import json
from unittest.mock import patch, MagicMock

class ChatbotTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('chat_api')

    @patch('myapp.views.genai')
    def test_chat_api_success(self, mock_genai):
        # Mock the Gemini API
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a simulated response about engineering."
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Mock configure to avoid actual network calls or key checks
        mock_genai.configure = MagicMock()

        # Payload
        data = {'message': 'Explain thermodynamics'}
        
        # Send POST request
        response = self.client.post(
            self.url, 
            json.dumps(data), 
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('response', response_data)
        self.assertEqual(response_data['response'], "This is a simulated response about engineering.")
        
        # Verify system prompt was used
        args, kwargs = mock_model.generate_content.call_args
        prompt_sent = args[0]
        self.assertIn("You are an AI tutor for engineering students", prompt_sent)
        self.assertIn("User: Explain thermodynamics", prompt_sent)

    def test_chat_api_no_message(self):
        response = self.client.post(
            self.url, 
            json.dumps({}), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_chat_api_invalid_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
