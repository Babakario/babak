import os
import json
import hmac
import hashlib
import base64
import logging
import requests
from datetime import datetime, timezone

# --- Configuration Loading ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WOOCOMMERCE_WEBHOOK_SECRET = os.getenv("WOOCOMMERCE_WEBHOOK_SECRET")

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Log to console
        # You can add logging.FileHandler("integration.log") here if needed
    ]
)

def check_configuration():
    """Checks if all necessary configurations are set."""
    missing_configs = []
    if not TELEGRAM_BOT_TOKEN:
        missing_configs.append("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_CHAT_ID:
        missing_configs.append("TELEGRAM_CHAT_ID")
    if not WOOCOMMERCE_WEBHOOK_SECRET:
        missing_configs.append("WOOCOMMERCE_WEBHOOK_SECRET")

    if missing_configs:
        error_message = f"Missing configuration variables: {', '.join(missing_configs)}"
        logging.critical(error_message)
        raise ValueError(error_message)
    logging.info("Configuration loaded successfully.")

# --- Webhook Signature Verification ---
def verify_signature(request_body_bytes: bytes, signature_header: str, secret: str) -> bool:
    """
    Verifies the WooCommerce webhook signature.

    Args:
        request_body_bytes: The raw request body (bytes).
        signature_header: The value of the X-WC-Webhook-Signature header.
        secret: The webhook secret key.

    Returns:
        True if the signature is valid, False otherwise.
    """
    if not signature_header:
        logging.warning("No signature header received.")
        return False
    if not secret:
        logging.error("Webhook secret is not configured. Cannot verify signature.")
        return False

    try:
        secret_bytes = secret.encode('utf-8')
        computed_hash = hmac.new(secret_bytes, request_body_bytes, hashlib.sha256)
        computed_signature = base64.b64encode(computed_hash.digest()).decode()

        if hmac.compare_digest(computed_signature, signature_header):
            logging.info("Webhook signature verified successfully.")
            return True
        else:
            logging.warning(f"Webhook signature mismatch. Expected: {computed_signature}, Got: {signature_header}")
            return False
    except Exception as e:
        logging.error(f"Error during signature verification: {e}")
        return False

# --- Order Data Parsing and Message Formatting ---
def format_order_message(order_data: dict) -> str:
    """
    Formats the order data from WooCommerce into a human-readable HTML message.

    Args:
        order_data: The parsed JSON payload from the WooCommerce webhook.

    Returns:
        A formatted string ready for Telegram.
    """
    try:
        order_id = order_data.get("id", "N/A")
        order_number = order_data.get("number", str(order_id)) # Fallback to id if number is not present

        date_created_str = order_data.get("date_created_gmt") or order_data.get("date_created")
        if date_created_str:
            try:
                # Parse ISO 8601 date string
                dt_object = datetime.fromisoformat(date_created_str.replace("Z", "+00:00"))
                # Convert to a more readable format, e.g., local timezone or just a clean UTC representation
                # For simplicity, let's format it as YYYY-MM-DD HH:MM:SS UTC
                order_date = dt_object.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
            except ValueError:
                logging.warning(f"Could not parse date: {date_created_str}")
                order_date = date_created_str # Fallback to original string
        else:
            order_date = "N/A"

        billing_info = order_data.get("billing", {})
        customer_first_name = billing_info.get("first_name", "")
        customer_last_name = billing_info.get("last_name", "")
        customer_name = f"{customer_first_name} {customer_last_name}".strip() or "N/A"
        customer_email = billing_info.get("email", "N/A")
        customer_phone = billing_info.get("phone", "N/A")

        address_1 = billing_info.get("address_1", "")
        address_2 = billing_info.get("address_2", "")
        city = billing_info.get("city", "")
        state = billing_info.get("state", "")
        postcode = billing_info.get("postcode", "")
        country = billing_info.get("country", "")

        full_address = f"{address_1}"
        if address_2:
            full_address += f"\n{address_2}"
        full_address += f"\n{city}, {state} {postcode}\n{country}".strip()
        if not full_address.strip().replace("\n", ""): # Check if address is essentially empty
            full_address = "N/A"


        line_items = order_data.get("line_items", [])
        items_list_str = ""
        if not line_items:
            items_list_str = "No items in order or items not provided in webhook.\n"
        else:
            for item in line_items:
                item_name = item.get("name", "N/A")
                quantity = item.get("quantity", "N/A")
                item_total = item.get("total", "N/A")
                items_list_str += f"- {quantity}x {item_name} (Total: {order_data.get('currency_symbol', '')}{item_total})\n"

        order_total = order_data.get("total", "N/A")
        currency_symbol = order_data.get("currency_symbol", "$") # Default to $ if not found

        message = (
            f"<b>🔔 New WooCommerce Order!</b>\n\n"
            f"<b>Order #:</b> {order_number}\n"
            f"<b>Date:</b> {order_date}\n\n"
            f"<b><u>👤 Customer:</u></b>\n"
            f"<b>Name:</b> {customer_name}\n"
            f"<b>Email:</b> {customer_email}\n"
            f"<b>Phone:</b> {customer_phone}\n\n"
            f"<b><u>📬 Billing Address:</u></b>\n"
            f"{full_address}\n\n"
            f"<b><u>🛍️ Items:</u></b>\n"
            f"{items_list_str}\n"
            f"<b>💰 Order Total: {currency_symbol}{order_total}</b>"
        )
        logging.info(f"Formatted message for order {order_number}")
        return message

    except Exception as e:
        logging.error(f"Error formatting order message: {e}", exc_info=True)
        return "Error: Could not format order details. Please check the logs."

# --- Telegram Message Sending ---
def send_telegram_message(bot_token: str, chat_id: str, message_text: str) -> bool:
    """
    Sends a message to a specified Telegram chat.

    Args:
        bot_token: The Telegram bot API token.
        chat_id: The target chat ID.
        message_text: The message text to send.

    Returns:
        True if the message was sent successfully, False otherwise.
    """
    if not bot_token or not chat_id:
        logging.error("Telegram Bot Token or Chat ID is not configured.")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

        response_json = response.json()
        if response_json.get("ok"):
            logging.info(f"Message successfully sent to Telegram chat ID {chat_id}.")
            return True
        else:
            logging.error(f"Telegram API error: {response_json.get('description')}")
            return False

    except requests.exceptions.Timeout:
        logging.error("Request to Telegram API timed out.")
        return False
    except requests.exceptions.ConnectionError:
        logging.error("Could not connect to Telegram API. Check network.")
        return False
    except requests.exceptions.HTTPError as e:
        logging.error(f"Telegram API HTTP error: {e.response.status_code} - {e.response.text}")
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"An unexpected error occurred while sending message to Telegram: {e}")
        return False
    except json.JSONDecodeError:
        logging.error(f"Could not decode JSON response from Telegram: {response.text}")
        return False


# --- Main Execution Flow (Conceptual - will be triggered by Flask) ---
if __name__ == "__main__":
    try:
        check_configuration()
        logging.info("Script initialized. Waiting for webhook events (via Flask).")
        # This part is for demonstration and direct testing if needed.
        # In a real scenario, a web framework like Flask will call handle_woocommerce_webhook.

        # Example Usage (for testing purposes - normally this data comes from Flask request):
        sample_order_data = {
            "id": 12345,
            "number": "WC-2024-12345",
            "date_created_gmt": "2024-07-30T10:30:00Z",
            "currency_symbol": "$",
            "total": "150.75",
            "billing": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "123-456-7890",
                "address_1": "123 Main St",
                "address_2": "Apt 4B",
                "city": "Anytown",
                "state": "CA",
                "postcode": "90210",
                "country": "US"
            },
            "line_items": [
                {"name": "Awesome T-Shirt", "quantity": 2, "total": "50.50"},
                {"name": "Cool Mug", "quantity": 1, "total": "25.25"},
                {"name": "Another Product", "quantity": 3, "total": "75.00"}
            ]
        }

        logging.info("Simulating webhook data for testing...")
        formatted_msg = format_order_message(sample_order_data)
        logging.info(f"Formatted test message:\n{formatted_msg}")

        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID: # Only send if configured
             if send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, formatted_msg):
                 logging.info("Test message sent successfully to Telegram.")
             else:
                 logging.error("Failed to send test message to Telegram.")
        else:
            logging.warning("Telegram token or chat ID not set, skipping sending test message.")

    except ValueError as ve:
        # Configuration errors already logged by check_configuration()
        # Exit or handle as appropriate for a script not yet in a server context
        pass
    except Exception as e:
        logging.critical(f"Unhandled exception in main: {e}", exc_info=True)

# The actual webhook listener will be set up in the Flask app script.
# This script provides the core functions to be called by that Flask app.
# For example, Flask app route would call:
#
# from flask import Flask, request, abort
# from woocommerce_telegram_integration import (
#     verify_signature, format_order_message, send_telegram_message,
#     TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, WOOCOMMERCE_WEBHOOK_SECRET,
#     check_configuration, logging
# )
#
# app = Flask(__name__)
#
# try:
#     check_configuration()
# except ValueError:
#     logging.critical("Application exiting due to missing configuration.")
#     exit(1) # Or handle differently if Flask should start but be non-operational
#
# @app.route('/webhook/woocommerce', methods=['POST'])
# def woocommerce_webhook():
#     signature = request.headers.get('X-WC-Webhook-Signature')
#     raw_body = request.data
#
#     if not verify_signature(raw_body, signature, WOOCOMMERCE_WEBHOOK_SECRET):
#         logging.warning("Webhook signature verification failed.")
#         abort(401) # Unauthorized
#
#     logging.info("Webhook signature verified. Processing order.")
#     order_data = request.json
#     if order_data.get('id'): # Basic check for order data
#         formatted_message = format_order_message(order_data)
#         send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, formatted_message)
#         return '', 200
#     else:
#         logging.error("Received webhook data does not look like an order.")
#         return '', 400 # Bad Request if data is not as expected

# if __name__ == '__main__':
#     # This is usually for running Flask app, not the script directly for webhooks
#     # app.run(debug=True, port=5000) # Example
#     logging.info("Script is designed to be imported by a web server like Flask.")
