# WooCommerce to Telegram Order Notifier

A Python application that sends notifications to a Telegram chat when a new order is created in your WooCommerce store. This helps you stay updated on new sales in real-time.

## Features

*   **Real-time Notifications:** Get instant alerts in Telegram for new WooCommerce orders.
*   **Secure Webhook Verification:** Uses a shared secret to ensure webhooks are genuinely from your WooCommerce store (HMAC-SHA256).
*   **Customizable:** Configure your own Telegram bot and target chat ID.
*   **Formatted Messages:** Order details are sent as well-formatted HTML messages in Telegram for easy readability.
*   **Comprehensive Details:** Notifications include Order ID, Date/Time, Customer Information (Name, Email, Phone), Billing Address, and a list of Products (Name, Quantity, Total).

## Requirements

*   Python 3.7+
*   A WooCommerce-enabled WordPress website.
*   A Telegram account.
*   A Telegram Bot (you'll create this).
*   A publicly accessible server or environment to host the Python script. For local testing, `ngrok` can be used.
*   `pip` for installing Python packages.

## File Structure

```
.
├── app.py                           # Flask web server to handle webhooks
├── woocommerce_telegram_integration.py # Core logic for verification, formatting, and sending
├── requirements.txt                 # Python dependencies
├── .env.example                     # Example environment variable file (you create .env)
└── README.md                        # This file
```
*(Note: You will need to create a `.env` file for your actual secrets based on `.env.example` or direct environment configuration.)*

## Setup and Configuration

Follow these steps to set up and configure the integration:

### 1. Get the Code

Clone this repository or download the files to your server/local machine.
```bash
# If it's a git repository:
# git clone <repository_url>
# cd <repository_name>
```

### 2. Install Dependencies

It's highly recommended to use a Python virtual environment.

```bash
# Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Create Your Telegram Bot

You need a Telegram bot to send notifications.

1.  **Open Telegram** and search for `BotFather` (official bot with a blue checkmark).
2.  Start a chat with BotFather by typing `/start`.
3.  Send `/newbot` to BotFather.
4.  Follow the prompts:
    *   Choose a **name** for your bot (e.g., "My Store Notifier").
    *   Choose a **username** for your bot (must end in "bot", e.g., `mystorenotifier_bot`). This username must be unique.
5.  BotFather will provide an **HTTP API token**. This token is very important and must be kept confidential.
6.  **Copy this token.** This will be your `TELEGRAM_BOT_TOKEN`.

### 4. Find Your Telegram Chat ID

This is the ID of the chat (your personal chat or a group) where the bot will send notifications.

*   **For Personal Notifications:**
    1.  After creating your bot, find it in Telegram using its username and send it any message (e.g., `/start`).
    2.  Search for a utility bot like `@get_id_bot` or `@userinfobot`.
    3.  Forward any message *from your bot* to the utility bot.
    4.  The utility bot will reply with your user information, including your **Chat ID** (often just "Id"). Copy this ID.
*   **For Group Notifications:**
    1.  Add your newly created bot to the Telegram group.
    2.  Send a message in the group (e.g., `/my_id@your_bot_username` if your bot is programmed to respond, or use a utility bot like `@get_id_bot` temporarily in the group).
    3.  The group's Chat ID will be a **negative number** (e.g., `-100123456789`). Copy this ID.

This ID will be your `TELEGRAM_CHAT_ID`.

### 5. Set Up Environment Variables

Create a `.env` file in the root of your project for local development. For production, set these variables directly in your hosting environment.

1.  You can copy `.env.example` to `.env` if an example file is provided, or create `.env` from scratch.
2.  Add the following, replacing the placeholder values with your actual credentials and a strong secret you create:

    ```env
    TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
    TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID_HERE
    WOOCOMMERCE_WEBHOOK_SECRET=CREATE_A_STRONG_RANDOM_SECRET_HERE
    # Optional for local Flask debugging:
    # FLASK_DEBUG=True
    # PORT=5000
    ```
    *   For `WOOCOMMERCE_WEBHOOK_SECRET`, generate a strong random string (e.g., using a password manager or online generator).

3.  **IMPORTANT:** Add `.env` to your `.gitignore` file to prevent committing secrets:
    ```
    .env
    venv/
    __pycache__/
    *.pyc
    ```

### 6. Configure WooCommerce Webhook

1.  In your WordPress admin dashboard, navigate to `WooCommerce > Settings > Advanced > Webhooks`.
2.  Click "**Add webhook**".
3.  Fill in the details:
    *   **Name:** A descriptive name (e.g., "Telegram Order Notifications").
    *   **Status:** Set to `Active`.
    *   **Topic:** Select `Order created`.
    *   **Delivery URL:** The public URL where your Flask app will be running and listening for webhooks. This URL must end with `/webhook` (e.g., `https://yourdomain.com/webhook` or your `ngrok` URL for testing).
    *   **Secret:** Enter the **exact same** string you used for `WOOCOMMERCE_WEBHOOK_SECRET` in your environment variables. This is crucial for verifying the webhook's authenticity.
    *   **API version:** Usually "WP REST API Integration v3" (default).
4.  Click "**Save webhook**".

## Running the Application

### Local Development & Testing

1.  Ensure your `.env` file is correctly configured.
2.  Start the Flask application:
    ```bash
    python app.py
    ```
    The app will typically run on `http://localhost:5000` (or the port specified by the `PORT` environment variable if you set one).
3.  **Expose local server with `ngrok`:**
    *   Download and run `ngrok`: `ngrok http 5000` (if your app is on port 5000).
    *   `ngrok` will give you a public HTTPS URL (e.g., `https://<random-string>.ngrok-free.app`).
    *   Use this `ngrok` URL + `/webhook` (e.g., `https://<random-string>.ngrok-free.app/webhook`) as the "Delivery URL" in your WooCommerce webhook settings for testing.

### Production Deployment

For production, **do not use the Flask development server (`app.run()`)**.

*   **WSGI Server:** Use a production-grade WSGI server like Gunicorn or uWSGI.
    *   Example Gunicorn command:
        ```bash
        gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
        ```
        (Adjust `workers` and `bind` address/port as needed.)
*   **Reverse Proxy (Recommended):** Set up Nginx or Apache in front of your WSGI server to handle incoming requests, SSL/TLS termination (HTTPS), and serve static files if any.
*   **Process Management:** Use `systemd` or `supervisor` to ensure your application runs continuously and restarts on failure.
*   **Platform as a Service (PaaS):** Consider deploying to platforms like Heroku, Google App Engine, AWS Elastic Beanstalk, or PythonAnywhere. These platforms often streamline the deployment process.
    *   Configure environment variables through the PaaS provider's dashboard.
    *   Ensure your `requirements.txt` is up to date.
    *   You might need a `Procfile` (e.g., for Heroku: `web: gunicorn app:app`).

## Testing the Integration

1.  Ensure your Python application is running and accessible at the "Delivery URL" configured in WooCommerce.
2.  Place a test order in your WooCommerce store.
3.  Within a few moments, you should receive a notification message in your configured Telegram chat.

## Troubleshooting

If you don't receive a notification:

1.  **Check Application Logs:**
    *   Look at the console output of your running `app.py` or the log files if you've configured file logging.
    *   Look for errors related to signature verification, message formatting, or sending messages to Telegram.
2.  **Check WooCommerce Webhook Logs:**
    *   In WordPress, go to `WooCommerce > Status > Logs`.
    *   Select the `webhooks-delivery-...` log from the dropdown (the name might vary slightly).
    *   Look for entries corresponding to your test order. It will show the request, response, and any delivery errors from WooCommerce's perspective.
3.  **Common Issues:**
    *   **Secrets Mismatch:** Ensure `WOOCOMMERCE_WEBHOOK_SECRET` in your `.env` file (or server environment) exactly matches the "Secret" field in the WooCommerce webhook settings.
    *   **Incorrect Delivery URL:** Verify the URL is correct, publicly accessible, and includes the `/webhook` path. If using `ngrok`, ensure it's still running and the URL hasn't changed.
    *   **Telegram Bot Token or Chat ID Incorrect:** Double-check these values in your environment variables.
    *   **Bot Not in Group/Chat:** If sending to a group, ensure the bot is a member of that group. If sending to yourself, ensure you've started a chat with the bot first.
    *   **Firewall Issues:** If self-hosting, ensure your server's firewall allows incoming connections on the port your application is using.
    *   **Python Dependencies:** Make sure all dependencies from `requirements.txt` are installed in your active Python environment.
    *   **JSON Payload Issues:** WooCommerce webhook payloads can sometimes vary based on plugins or versions. The script extracts common fields; if a field is missing in your specific payload, `format_order_message` might show "N/A" or error out if not handled gracefully (the current script uses `.get()` for safety). Check the logs for data extraction issues.

## How It Works (Briefly)

1.  When a new order is created in WooCommerce, it triggers the configured webhook.
2.  WooCommerce sends an HTTP POST request containing the order data (JSON payload) to the "Delivery URL" you specified. The request includes a signature in the `X-WC-Webhook-Signature` header.
3.  Your Flask application (`app.py`), running at the Delivery URL, receives this request at the `/webhook` endpoint.
4.  The application verifies the signature using the `WOOCOMMERCE_WEBHOOK_SECRET` to ensure the request is authentic.
5.  If the signature is valid, the script (`woocommerce_telegram_integration.py`) parses the order data.
6.  The order details are formatted into a human-readable HTML message.
7.  This formatted message is then sent to the specified `TELEGRAM_CHAT_ID` using your `TELEGRAM_BOT_TOKEN` via the Telegram Bot API.

---
