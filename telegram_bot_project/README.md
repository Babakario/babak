# Web3 Airdrop Campaign Telegram Bot

This Telegram bot is designed to manage an airdrop campaign, allowing users to complete tasks, earn points, and connect their Web3 wallets. Admins can manage tasks and view user progress.

## Features

*   User registration and wallet connection.
*   Task management with reward points.
*   Daily active task system.
*   Admin panel for adding/removing tasks and managing daily tasks.
*   Reward calculation for users.
*   MongoDB integration for data persistence.
*   Scheduled jobs for daily task refreshes.

## Project Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd telegram_bot_project
    ```

2.  **Install Dependencies:**
    ```bash
    npm install
    ```

3.  **Create `.env` File:**
    Create a file named `.env` in the `telegram_bot_project` root directory. Add the following environment variables:

    *   `TELEGRAM_BOT_TOKEN`: Your Telegram Bot Token obtained from BotFather. This is essential for the bot to connect to Telegram.
    *   `MONGODB_URI`: Your MongoDB connection string (e.g., `mongodb://localhost:27017/airdrop_bot` or a cloud MongoDB instance URI). This is where all user and task data will be stored.
    *   `ADMIN_TELEGRAM_ID`: The Telegram User ID of the bot administrator. This ID is used to grant access to admin commands. You can get your ID by messaging a bot like `@userinfobot` on Telegram.

    Example `.env` content:
    ```env
    TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1uT0
    MONGODB_URI=mongodb://localhost:27017/airdrop_bot
    ADMIN_TELEGRAM_ID=YOUR_TELEGRAM_USER_ID
    ```

## Running the Bot Locally

1.  Ensure MongoDB is running and accessible with the URI provided in `.env`.
2.  Start the bot:
    ```bash
    node index.js
    ```
    You should see console logs indicating the bot has started and connected to the database, along with a message about the scheduled daily task refresh.

## Manual Testing Checklist

### User Registration & Wallet
*   **`/start`**:
    *   Send `/start` to the bot.
    *   Expected: Bot replies with a welcome message. If it's a new user, their profile is created in the database.
*   **`/connectwallet`**:
    *   Send `/connectwallet`.
    *   Expected: Bot prompts for an Ethereum wallet address.
    *   Reply with a valid Ethereum address (e.g., `0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B`).
    *   Expected: Bot confirms address received and stored. If a `WALLET_CONNECT` type task exists and is active, it should be automatically marked as complete.
    *   Reply with an invalid address (e.g., `notAnAddress` or `0x123`).
    *   Expected: Bot informs the user the address is invalid.

### Task Interaction
*   **`/tasks`**:
    *   Send `/tasks`.
    *   Expected: Bot lists only daily active tasks. Each task should show its description, reward points, ID, and completion status for the user (✅ for completed, ☑️ for pending).
*   **`/complete <task_id>`**:
    *   Identify a `task_id` from the `/tasks` list (that isn't auto-completed like wallet connect).
    *   Send `/complete <task_id>` (e.g., `/complete TELEGRAM_JOIN_1`).
    *   Expected: Bot confirms the task is marked as complete.
    *   Send `/tasks` again.
    *   Expected: The completed task now shows ✅.
*   **`/myrewards`**:
    *   Send `/myrewards`.
    *   Expected: Bot displays the total accumulated reward points based on completed tasks. If no tasks are completed, it should show 0 points.

### Admin Functionality (Requires `ADMIN_TELEGRAM_ID` in `.env` to be set to your Telegram ID)
*   **Access Control:**
    *   From a non-admin Telegram account, try an admin command (e.g., `/addtask TEST 10 true Test desc`).
    *   Expected: Bot replies with "Access Denied."
*   **`/addtask <type> <points> <isDailyActive:true|false> <description>`**:
    *   Example: `/addtask GENERAL 15 true Visit our new website`
    *   Expected: Bot confirms task added with a `customId`.
    *   Send `/tasks`. If `isDailyActive` was `true`, the new task should appear. If `false`, it should not.
*   **`/removetask <task_id>`**:
    *   Use the `customId` of a task (e.g., one added above or a default one).
    *   Example: `/removetask GENERAL_16...`
    *   Expected: Bot confirms task removal.
    *   Send `/tasks`. The task should no longer be listed.
*   **`/settaskdaily <task_id>`**:
    *   Identify a task that is not currently daily active (e.g., `WALLET_CONNECT_1` by default, or one added with `false`).
    *   Example: `/settaskdaily WALLET_CONNECT_1`
    *   Expected: Bot confirms the task is now daily active.
    *   Send `/tasks`. The task should now appear in the list for users.
*   **`/unsettaskdaily <task_id>`**:
    *   Identify a task that is currently daily active.
    *   Example: `/unsettaskdaily TELEGRAM_JOIN_1`
    *   Expected: Bot confirms the task is no longer daily active.
    *   Send `/tasks`. The task should no longer appear in the list for users.

### Scheduled Job
*   **Startup:**
    *   Observe the console when starting the bot (`node index.js`).
    *   Expected: A message like "Daily task refresh job scheduled for midnight UTC."
*   **Execution (Requires waiting or simulating the cron time):**
    *   At midnight UTC (or the configured time), check the bot's console output.
    *   Expected: A message like "Scheduled daily task refresh: Checking active daily tasks..." followed by the count of daily active tasks.

## Automated Testing (Future Enhancement)

While this project currently relies on manual testing, incorporating automated tests is highly recommended for future development and ensuring stability.

*   **Consider using a test framework like Jest or Mocha.**
*   **Install Jest:**
    ```bash
    npm install --save-dev jest
    ```
*   **Create a `tests` directory** for test files (e.g., `telegram_bot_project/tests/database.test.js`, `telegram_bot_project/tests/bot.test.js`).
*   **Unit tests** should cover functions in `database.js`. This typically involves mocking MongoDB interactions (e.g., using `mongodb-memory-server` or Jest's mocking capabilities). Utility functions within `index.js` (like `isAdmin`) can also be unit tested.
*   **Integration tests** can simulate command flows by mocking the TelegramBot API or parts of it to verify that commands trigger the correct database operations and bot replies.

## Deployment

### Environment Variables
Ensure the following environment variables are set in your production/hosting environment:
*   `TELEGRAM_BOT_TOKEN`
*   `MONGODB_URI` (use a production MongoDB instance)
*   `ADMIN_TELEGRAM_ID`

### Process Management
For running the bot continuously in production, using a process manager like PM2 is recommended.
*   **Install PM2 globally:**
    ```bash
    npm install pm2 -g
    ```
*   **Start the bot with PM2:**
    ```bash
    pm2 start index.js --name airdrop-bot
    ```
*   **Monitoring:**
    *   List running processes: `pm2 list`
    *   View logs: `pm2 logs airdrop-bot`
    *   Other useful commands: `pm2 restart airdrop-bot`, `pm2 stop airdrop-bot`, `pm2 delete airdrop-bot`.

### Logging
For production environments, consider using a more robust logging library than `console.log` for better log management, formatting, and destinations (e.g., file, logging services). Examples include Winston or Pino.

### Platforms
You can deploy this Node.js application to various hosting platforms, including:
*   Heroku (using the `Procfile` provided)
*   AWS (EC2, Elastic Beanstalk, Fargate)
*   DigitalOcean (Droplets, App Platform)
*   Google Cloud (Compute Engine, App Engine, Cloud Run)
*   Railway
*   Render

### Dockerfile (Optional)
For containerized deployments, you can use Docker. Below is a basic example `Dockerfile`:

```dockerfile
# Dockerfile Example
FROM node:18-alpine

WORKDIR /usr/src/app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
COPY package*.json ./
RUN npm install --production # Use --production for smaller image size if devDeps not needed

# Bundle app source
COPY . .

# Environment variables - It's better to set these at runtime via your hosting platform
# ENV TELEGRAM_BOT_TOKEN=your_token_here
# ENV MONGODB_URI=your_mongo_uri_here
# ENV ADMIN_TELEGRAM_ID=your_admin_id_here

# Expose port if your app were a web server (not strictly necessary for a Telegram bot worker)
# EXPOSE 3000

CMD [ "node", "index.js" ]
```
**Note:** For environment variables in Docker, it's best practice to provide them at runtime (e.g., via `docker run -e VAR=value` or through your container orchestration platform) rather than hardcoding them in the Dockerfile, especially for sensitive values. The `ENV` lines in the example are illustrative.

---

This `README.md` provides a comprehensive guide for setting up, running, testing, and deploying the bot.
