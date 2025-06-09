import requests
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_telegram_message(bot_token: str, chat_id: str, text: str) -> bool:
    """
    Sends a message to a specified Telegram chat using the Telegram Bot API.

    Args:
        bot_token: The token of the Telegram bot.
        chat_id: The ID of the chat to send the message to.
        text: The message text to send.

    Returns:
        True if the message was sent successfully, False otherwise.
    """
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}

    try:
        response = requests.post(api_url, json=payload, timeout=10)
        if response.ok:
            logging.info(f"Successfully sent message to chat_id: {chat_id}")
            return True
        else:
            logging.error(
                f"Failed to send message to chat_id: {chat_id}. "
                f"Status Code: {response.status_code}, Response: {response.text}"
            )
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending Telegram message to chat_id: {chat_id}. Exception: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while sending Telegram message to chat_id: {chat_id}. Exception: {e}")
        return False
