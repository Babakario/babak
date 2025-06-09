import unittest
from unittest.mock import patch
import requests # For requests.exceptions.RequestException
from app.services.telegram_service import send_telegram_message

class TestSendTelegramMessage(unittest.TestCase):

    @patch('app.services.telegram_service.requests.post')
    def test_send_telegram_message_success(self, mock_post):
        # Configure mock_post to simulate a successful response
        mock_response = mock_post.return_value
        mock_response.ok = True
        mock_response.status_code = 200
        # mock_response.json.return_value = {'ok': True, 'result': 'message_sent'} # Not strictly needed as send_telegram_message doesn't parse json on success

        result = send_telegram_message('fake_token', '12345', 'Hello')
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            'https://api.telegram.org/botfake_token/sendMessage',
            json={'chat_id': '12345', 'text': 'Hello'},
            timeout=10
        )

    @patch('app.services.telegram_service.requests.post')
    def test_send_telegram_message_telegram_api_error(self, mock_post):
        # Configure mock_post to simulate a Telegram API error
        mock_response = mock_post.return_value
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'

        result = send_telegram_message('fake_token', '12345', 'Hello')
        self.assertFalse(result)
        mock_post.assert_called_once_with(
            'https://api.telegram.org/botfake_token/sendMessage',
            json={'chat_id': '12345', 'text': 'Hello'},
            timeout=10
        )

    @patch('app.services.telegram_service.requests.post')
    def test_send_telegram_message_request_exception(self, mock_post):
        # Configure mock_post to raise a request exception
        mock_post.side_effect = requests.exceptions.RequestException('Network error')

        result = send_telegram_message('fake_token', '12345', 'Hello')
        self.assertFalse(result)
        mock_post.assert_called_once_with(
            'https://api.telegram.org/botfake_token/sendMessage',
            json={'chat_id': '12345', 'text': 'Hello'},
            timeout=10
        )

    @patch('app.services.telegram_service.requests.post')
    def test_send_telegram_message_unexpected_exception(self, mock_post):
        # Configure mock_post to raise an unexpected exception
        mock_post.side_effect = Exception('Unexpected error')

        result = send_telegram_message('fake_token', '12345', 'Hello')
        self.assertFalse(result)
        mock_post.assert_called_once_with(
            'https://api.telegram.org/botfake_token/sendMessage',
            json={'chat_id': '12345', 'text': 'Hello'},
            timeout=10
        )

if __name__ == '__main__':
    unittest.main()
