# Python Telegram Bot

This project contains a Python-based Telegram bot.

## Setup and Running

1.  **Install Dependencies**:
    Install the required Python libraries using pip:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure API Token**:
    Open the `telegram_bot.py` file. Find the line:
    ```python
    TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    ```
    Replace `"YOUR_TELEGRAM_BOT_TOKEN_HERE"` with your actual Telegram Bot Token obtained from @BotFather.

3.  **Run the Bot**:
    Execute the bot script from your terminal:
    ```bash
    python telegram_bot.py
    ```
    The bot will start polling for messages.

## Notes on Bot Features (Compared to PHP Instructions)

*   **API Token**: Instead of a `validate.php` file, the Telegram API token is placed directly into the `telegram_bot.py` script.
*   **Menu Buttons**: The concept of setting a "Menu Button URL" via BotFather (common for web-based PHP bots) is handled differently in `python-telegram-bot`. Interactive menus are typically created using:
    *   **Bot Commands**: Like the `/start` command already implemented.
    *   **Inline Keyboards**: Buttons that appear directly under a message.
    *   **Reply Keyboards**: Custom keyboards that replace the standard user keyboard.
    These are defined in the bot's Python code.
*   **User Management**: An admin panel like `admin.php` for viewing users is not included by default. This functionality would need to be developed separately (e.g., by storing user data in a database and creating specific admin commands for the bot).
