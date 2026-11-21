from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from unittest.mock import patch
from .models import ConversacionIA
import json


class LlmChatApiTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='llmtest', password='test-1234')
        self.client = Client()
        self.client.login(username='llmtest', password='test-1234')

    def test_chat_sin_clave_retorna_error_controlado(self):
        with patch.dict('os.environ', {'GROQ_API_KEY': ''}):
            response = self.client.post('/llm/api/chat/', json.dumps({'message': '¿Qué stock está crítico?'}), content_type='application/json')
        self.assertEqual(response.status_code, 503)
        self.assertIn('GROQ_API_KEY', response.json()['error'])

    def test_mensaje_vacio_retorna_bad_request(self):
        response = self.client.post('/llm/api/chat/', json.dumps({'message': ''}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
