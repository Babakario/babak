import os
import logging
from flask import Flask, request, abort

# Attempt to import from the local integration script
try:
    from woocommerce_telegram_integration import (
        verify_signature,
        format_order_message,
        send_telegram_message,
        check_configuration as check_integration_config, # Renamed to avoid conflict
        TELEGRAM_BOT_TOKEN,
        TELEGRAM_CHAT_ID,
        WOOCOMMERCE_WEBHOOK_SECRET
    )
except ImportError:
    logging.critical("Failed to import 'woocommerce_telegram_integration.py'. "
                     "Ensure it's in the same directory or Python path.")
    exit(1)

app = Flask(__name__)

# --- Logging Setup ---
# Basic logging is already configured in woocommerce_telegram_integration.py
# We can add Flask specific logging or rely on that.
# For simplicity, we'll use the one configured in the imported module.
# If more specific Flask logging is needed, it can be added here.
# Example:
# if not app.debug:
#     app.logger.setLevel(logging.INFO)
#     handler = logging.StreamHandler()
#     handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
#     app.logger.addHandler(handler)

# --- Configuration Check ---
try:
    # This function from the integration script now handles checking critical env vars
    check_integration_config()
    # Specifically load them for Flask app's direct use if needed, though they are also top-level in the other module
    # This is more for clarity if Flask app needs them directly, otherwise the imported ones are fine.
    FLASK_WOOCOMMERCE_WEBHOOK_SECRET = WOOCOMMERCE_WEBHOOK_SECRET
    FLASK_TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN
    FLASK_TELEGRAM_CHAT_ID = TELEGRAM_CHAT_ID

    if not all([FLASK_WOOCOMMERCE_WEBHOOK_SECRET, FLASK_TELEGRAM_BOT_TOKEN, FLASK_TELEGRAM_CHAT_ID]):
        # This is a redundant check if check_integration_config() is thorough, but good for defense in depth
        logging.critical("One or more critical configurations are missing after initial check. This should not happen.")
        exit(1)
    logging.info("Flask app configuration loaded successfully.")

except ValueError as e:
    logging.critical(f"Application exiting due to missing configuration: {e}")
    # The check_integration_config already logs and raises ValueError.
    # We exit here to prevent Flask from starting with missing critical configs.
    exit(1)
except Exception as e:
    logging.critical(f"An unexpected error occurred during Flask app initialization: {e}", exc_info=True)
    exit(1)


@app.route('/')
def home():
    return "WooCommerce to Telegram Integration is running.", 200

@app.route('/webhook', methods=['POST'])
def woocommerce_webhook():
    logging.info("Webhook endpoint hit.")

    # Get signature from header
    signature_header = request.headers.get('X-WC-Webhook-Signature')
    if not signature_header:
        logging.warning("Request missing X-WC-Webhook-Signature header.")
        abort(400, description="Missing X-WC-Webhook-Signature header.")

    # Get raw request body
    request_body_bytes = request.data

    # Verify signature
    if not verify_signature(request_body_bytes, signature_header, FLASK_WOOCOMMERCE_WEBHOOK_SECRET):
        logging.warning("Webhook signature verification failed.")
        abort(401, description="Invalid webhook signature.")

    logging.info("Webhook signature verified successfully.")

    # Process the webhook data
    try:
        order_data = request.json
        if not order_data:
            logging.error("Received empty JSON payload or non-JSON data.")
            abort(400, description="Invalid JSON payload.")

        # Check if it's an order-related event, specifically 'order.created' if possible
        # The topic is usually in X-WC-Webhook-Topic header, or one can infer from payload structure.
        # For now, we assume any valid, signed payload with an 'id' is an order.
        # A more robust check might involve inspecting order_data['topic'] if available or specific fields.

        webhook_topic = request.headers.get('X-WC-Webhook-Topic', 'N/A')
        logging.info(f"Processing webhook for topic: {webhook_topic}")

        # You might want to filter for specific topics, e.g., 'order.created'
        # if webhook_topic != 'order.created':
        #     logging.info(f"Ignoring webhook topic: {webhook_topic}")
        #     return 'Webhook topic ignored', 200

        if "id" in order_data: # A simple check to see if it looks like order data
            logging.info(f"Processing order ID: {order_data.get('id')}")

            formatted_message = format_order_message(order_data)

            if "Error: Could not format order details." in formatted_message:
                logging.error("Failed to format order message. Check previous logs.")
                # Still return 200 to WooCommerce as the webhook was valid, but log internal error.
                return 'Internal error formatting message', 200

            if send_telegram_message(FLASK_TELEGRAM_BOT_TOKEN, FLASK_TELEGRAM_CHAT_ID, formatted_message):
                logging.info("Successfully processed webhook and sent Telegram message.")
            else:
                logging.error("Failed to send Telegram message after processing webhook.")
                # Again, return 200 to WC as the webhook itself was fine.
        else:
            logging.warning("Received webhook data does not appear to be a valid order (missing 'id').")
            # Consider if this should be a 400 or a 200 if it's a valid webhook but not an order
            return 'Webhook received but not an order or missing ID', 200

        return 'Webhook processed successfully', 200

    except Exception as e:
        logging.error(f"Error processing webhook payload: {e}", exc_info=True)
        # Don't send 500 to WooCommerce if possible, as it might retry indefinitely.
        # Log the error and respond 200 if the webhook was valid but internal processing failed.
        # If the error is due to bad request data (e.g. not JSON), Flask might handle it before this.
        return 'Error processing webhook', 200 # Or 500 if appropriate for your retry strategy

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # Set debug=False for production
    # Use a production-ready WSGI server like Gunicorn or uWSGI instead of app.run() in production
    app.run(host='0.0.0.0', port=port, debug=os.environ.get("FLASK_DEBUG", "False").lower() == "true")
