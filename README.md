# babak

## Anonymous Telegram Bot

This feature allows users to receive anonymous messages via a Telegram bot. Users can generate a unique link to share, and anyone with the link can send them messages without revealing their identity.

### Environment Variables

To run the Telegram bot functionality, you need to set the following environment variables:

*   `BOT_TOKEN`: Your Telegram Bot Token obtained from BotFather.
*   `BOT_ID`: Your Telegram Bot's username (e.g., `your_anon_bot`) *without* the leading `@`.

The application is configured to use a SQLite database located at `sqlite:///project.db` (defined in `app/__init__.py`). This file will be created automatically in the project root if it doesn't exist when the app starts.

### Setup and Running

1.  **Install Dependencies:**
    Open your terminal and navigate to the project directory. Run:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set Environment Variables:**
    Set the `BOT_TOKEN` and `BOT_ID` environment variables. How you do this depends on your operating system:
    *   Linux/macOS:
        ```bash
        export BOT_TOKEN="your_actual_bot_token"
        export BOT_ID="your_bot_username"
        ```
    *   Windows (Command Prompt):
        ```bash
        set BOT_TOKEN="your_actual_bot_token"
        set BOT_ID="your_bot_username"
        ```
    *   Windows (PowerShell):
        ```bash
        $env:BOT_TOKEN="your_actual_bot_token"
        $env:BOT_ID="your_bot_username"
        ```
    Alternatively, you can use a `.env` file with a library like `python-dotenv` (not currently included in `requirements.txt`) or set them directly in your `run.py` for development (not recommended for production).

3.  **Run the Application:**
    ```bash
    python run.py
    ```
    The Flask application will typically start on `http://127.0.0.1:5000/`.

### Webhook Initialization

After starting the application for the first time (or if your bot token/domain changes), you need to tell Telegram where to send updates (webhook).

1.  Ensure your Flask application is running.
2.  Open your web browser and go to:
    `http://127.0.0.1:5000/init_telegram_webhook`

    *   **Note:** This endpoint attempts to register a webhook URL with Telegram. For development, it tries to convert `http://127.0.0.1:5000/` to `https://127.0.0.1:5000/` (or similar based on `request.url_root`) for the `webhook_url` part of the Telegram API call. However, Telegram requires a publicly accessible HTTPS URL for webhooks to work reliably in production. For local development, you might need to use a tunneling service like ngrok to expose your local server to the internet via HTTPS and use that ngrok URL when setting the webhook (either manually via Telegram API or by modifying the `init_telegram_webhook` logic).
    *   The browser will display a JSON response from the Telegram API indicating success or failure.

This step only needs to be performed once unless your bot token changes or your application's public URL changes.

### How it Works

1.  **Get Your Link:** A user interacts with your bot on Telegram and sends the `/start` command. The bot responds with a unique link (e.g., `https://t.me/your_bot_username?start=randomkey`).
2.  **Share Your Link:** The user shares this unique link with friends or on social media.
3.  **Open Link & Send Message:**
    *   When someone else (User B) clicks this link, their Telegram client opens a chat with your bot, prefilled with `/start randomkey`.
    *   When User B sends this `/start randomkey` command, the bot recognizes that User B wants to send messages to the owner of `randomkey`.
    *   The bot then prompts User B to send their anonymous message.
4.  **Receive Anonymous Message:** Any message User B sends after this initial setup is forwarded anonymously by the bot to the original link owner (User A). User A sees the message as coming from the bot. User B receives a confirmation that their message was sent.
