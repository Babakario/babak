# Nobitex Price Bot - Cloudflare Worker for Telegram

This Cloudflare Worker fetches cryptocurrency prices from the Nobitex exchange API and sends them as updates to a specified Telegram chat. It can be configured to watch multiple coin pairs and runs on a schedule.

## Features

- Fetches latest prices from Nobitex for specified coin pairs.
- Sends formatted price updates to a Telegram chat.
- Supports multiple coin pairs.
- Runs on a configurable schedule using Cloudflare Worker cron triggers.
- Reports errors during operation to the Telegram chat.

## Prerequisites

1.  **Cloudflare Account:** You'll need a Cloudflare account.
2.  **Telegram Bot:**
    *   Create a new Telegram bot by talking to the [BotFather](https://t.me/BotFather).
    *   Note down the **Bot Token** provided by BotFather.
3.  **Telegram Chat ID:**
    *   You need the ID of the chat where the bot will send messages. This can be a personal chat or a group chat.
    *   To get your personal chat ID, send `/start` to your bot, then visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`. Look for the `chat.id` in the JSON response.
    *   For a group, add the bot to the group. Send a message in the group (e.g., `/my_id @your_bot_username`). Then check the `getUpdates` link. The chat ID will be a negative number.

## Files

1.  `index.js`: The main worker code.
2.  `wrangler.toml`: Configuration file for deploying with Wrangler. (Optional if using Dashboard only for cron).

## Setup and Deployment

You can deploy this worker using either the Cloudflare Dashboard or Wrangler CLI.

### Option 1: Using Wrangler CLI

1.  **Install Wrangler:**
    ```bash
    npm install -g wrangler
    # or
    yarn global add wrangler
    ```
2.  **Login to Wrangler:**
    ```bash
    wrangler login
    ```
3.  **Configure `wrangler.toml`:**
    *   Ensure `name` is unique for your worker.
    *   `main = "index.js"`
    *   `compatibility_date` should be a recent date.
    *   The `[[triggers]] crons = ["*/5 * * * *"]` line sets the schedule (every 5 minutes in this example). Adjust as needed.

4.  **Set Secrets (Environment Variables):**
    These are best set directly in the Cloudflare dashboard for security, or via Wrangler secrets.
    ```bash
    wrangler secret put TELEGRAM_BOT_TOKEN
    # (Paste your bot token when prompted)

    wrangler secret put TELEGRAM_CHAT_ID
    # (Paste your chat ID when prompted)
    ```

5.  **Deploy:**
    ```bash
    wrangler publish
    ```

### Option 2: Using the Cloudflare Dashboard

1.  **Create a Worker:**
    *   Log in to your Cloudflare dashboard.
    *   Navigate to "Workers & Pages".
    *   Click "Create application", then "Create Worker".
    *   Give your worker a unique name and click "Deploy".
2.  **Configure the Worker:**
    *   Click "Configure Worker" or "Edit code".
    *   Copy the content of `index.js` from this repository and paste it into the editor.
3.  **Add Environment Variables (Secrets):**
    *   Go to your worker's settings tab.
    *   Under "Environment Variables", click "Add variable".
    *   Create `TELEGRAM_BOT_TOKEN` and enter your bot token. Encrypt it if prompted.
    *   Create `TELEGRAM_CHAT_ID` and enter your chat ID. Encrypt it if prompted.
4.  **Set Cron Trigger:**
    *   In your worker's settings, go to the "Triggers" tab.
    *   Under "Cron Triggers", click "Add Cron Trigger".
    *   Enter your desired cron schedule (e.g., `*/5 * * * *` for every 5 minutes).
    *   Click "Add".

## Customization

### Changing Monitored Coins

1.  Open `index.js`.
2.  Locate the `COIN_PAIRS_TO_WATCH` array at the top of the file:
    ```javascript
    const COIN_PAIRS_TO_WATCH = ['USDT-RLS', 'BTC-RLS', 'ETH-RLS'];
    ```
3.  Modify this array to include the Nobitex market symbols you want to monitor (e.g., `'XRP-RLS'`, `'DOGE-USDT'`).
4.  Redeploy the worker if you've made changes.

### Changing the Schedule

-   **Wrangler:** Modify the `crons` array in `wrangler.toml` and run `wrangler publish`.
-   **Dashboard:** Go to your worker's "Triggers" tab and edit the Cron Trigger.

## Testing

-   After deployment, you can manually trigger the worker by visiting its URL (e.g., `your-worker-name.your-subdomain.workers.dev`). This should send a message to your Telegram chat.
-   Monitor your Telegram chat for scheduled updates.
-   Check the worker logs in the Cloudflare dashboard for any errors or messages.

## Nobitex API

This worker uses the public Nobitex API endpoint: `https://api.nobitex.ir/v2/orderbook/all`.
Refer to the [official Nobitex API documentation](https://nobitex.ir/docs/) for more details on available markets and data structures.
```
