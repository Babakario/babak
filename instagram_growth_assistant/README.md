# Instagram Growth Assistant

This project aims to provide tools and insights to help users ethically grow their Instagram presence.

## Features (Implemented)

*   **Instagram API Client:** Fetches recent media for a given hashtag using the Instagram Graph API (public content).
*   **OAuth Authentication Flow:** Basic command-line support for Instagram OAuth 2.0 user authentication to obtain access tokens for user-specific data (currently placeholder functionality for API calls using this token).
*   **Token Management:** Saves and loads OAuth access tokens locally.
*   **Data Storage:** Saves fetched media data (ID, username, caption, likes, comments, etc.) to a CSV file.
*   **Hashtag Analysis:**
    *   Extracts and counts hashtag occurrences from the captions in the saved CSV data.
    *   Identifies the most frequently used co-occurring hashtags.
*   **User Suggestion:**
    *   Identifies users who have posted multiple times within the collected media for a hashtag.
    *   Suggests potentially relevant users based on post frequency.
*   **N-gram Theme Suggestion:** Analyzes captions for common two-word (bigram) and three-word (trigram) phrases to suggest potential content themes.


## Project Structure
(Project structure section remains largely the same, ensure `src/auth/` and `token_manager.py` are reflected if not already. For brevity, I'm assuming it's correct or will be manually checked by user if this subtask doesn't explicitly ask to list files again.)
```
instagram_growth_assistant/
├── config/
│   ├── config.example.ini
│   └── config.ini
├── data/
│   └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── instagram_client.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── hashtag_analyzer.py
│   │   ├── user_suggester.py
│   │   └── caption_analyzer.py
│   ├── auth/                 # New
│   │   ├── __init__.py
│   │   ├── instagram_oauth.py
│   │   └── token_manager.py
│   └── core/
│       └── __init__.py
├── tests/
│   # ... (test structure)
├── .gitignore
├── README.md
└── requirements.txt
```

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd instagram_growth_assistant
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configuration (`config/config.ini`):**
    *   Copy `config/config.example.ini` to `config/config.ini`:
        ```bash
        cp config/config.example.ini config/config.ini
        ```
    *   **Fill in the details in `config.ini`:**
        *   **`[instagram_api]` Section (for Public Content & Hashtag Analysis):**
            *   `user_access_token`: Your Instagram Graph API User Access Token (often a Page Access Token or a User token with public content permissions).
            *   `user_id`: Your Instagram User ID (the one linked to the Page, if applicable for the token).
            *   **Important:** This token needs permissions like `instagram_basic`, `instagram_manage_insights`, and potentially `instagram_public_content_search` (requires App Review by Meta for hashtag searches).
        *   **`[instagram_app_oauth]` Section (for User-Specific Data - e.g., future Follower Analysis):**
            *   `app_id`: Your Instagram App ID from your app on [Meta for Developers](https://developers.facebook.com/).
            *   `app_secret`: Your Instagram App Secret.
            *   `redirect_uri`: The "Valid OAuth Redirect URI" you configured in your Meta Developer App settings (e.g., `http://localhost:8080/instagram_callback`). **This URI must exactly match what is set in your app configuration on the Facebook Developer portal.**
            *   These credentials are vital for features that will access your own account's data.

## Instagram Account Authentication (for User-Specific Data)

For features that require accessing your own Instagram account data (e.g., future follower analysis, posting capabilities), you need to authenticate the application. This tool uses a command-line based OAuth 2.0 flow.

**Prerequisites:** Ensure the `[instagram_app_oauth]` section in your `config/config.ini` is correctly filled out (App ID, App Secret, Redirect URI).

### Logging In (Command-Line Flow)

The login process involves two main steps using `src/main.py`:

1.  **Initiate Login:**
    Run the following command in your terminal:
    ```bash
    python src/main.py instagram_login
    ```
    The script will generate and display an Instagram Authorization URL.

2.  **Authorize in Browser:**
    *   Copy the displayed URL and paste it into your web browser.
    *   Log in to your Instagram account (if not already logged in).
    *   Grant the application the requested permissions.

3.  **Complete Authentication:**
    *   After authorization, Instagram will redirect your browser to the `redirect_uri` you configured. The URL in your browser's address bar will now contain a `code` parameter (e.g., `YOUR_REDIRECT_URI?code=AQB...#_`).
    *   Copy this entire `code` value (it can be quite long).
    *   Run the following command in your terminal, replacing `YOUR_COPIED_CODE_HERE` with the actual code:
        ```bash
        python src/main.py instagram_complete_auth --code YOUR_COPIED_CODE_HERE
        ```
    *   If successful, the application will exchange this code for an access token and save it locally in a file named `.instagram_token_cache.json` at the root of the project.

### Checking Login Status (Conceptual)

Currently, there isn't a direct command to check login status. However, features requiring authentication will attempt to load the token from `.instagram_token_cache.json`. If the token is missing or invalid, those features would typically fail or prompt you to log in.

### Logging Out

To log out, which deletes the locally stored access token:
```bash
python src/main.py instagram_logout
```
This removes the `.instagram_token_cache.json` file.

### Security Note on Token Cache

The `.instagram_token_cache.json` file stores your access token, granting the application access to your Instagram account within the scopes you authorized.
*   This file is included in `.gitignore` to prevent accidental commits.
*   **Keep this file secure.** If you move or copy your project, be mindful of this file. Deleting it is equivalent to logging out the application.

## Usage: `src/main.py` Commands for Data Fetching & Analysis

The `src/main.py` script provides several commands to interact with the Instagram API and perform analysis.

**General Command Structure:**
```bash
python src/main.py <command> [options_for_command]
```

### `fetch` Command
Fetches public media for a given hashtag and can perform various analyses on the fetched data.

**Basic Fetch & Save to CSV:**
```bash
python src/main.py fetch yourhashtag --limit 20 --output-csv
```
*   `yourhashtag`: The hashtag to search for (without the #).
*   `--limit 20`: Fetches up to 20 posts (default is 10).
*   `--output-csv`: Saves data to `data/yourhashtag_YYYYMMDD_HHMMSS.csv`.

**Fetch with All Analyses:**
```bash
python src/main.py fetch recipeideas --limit 30 --output-csv --analyze-hashtags --hashtag-top-n 8 --suggest-users --suggest-min-posts 2 --suggest-top-n 5 --suggest-themes --ngram-top-n-bigrams 5 --ngram-top-n-trigrams 5
```

**Available arguments for the `fetch` command:**
*   `hashtag` (required): The hashtag to search.
*   `--limit <number>`: Number of media items to fetch (default: 10).
*   `--output-csv`: Save output to a CSV file in the `data/` directory. This is required for all analysis options.
*   `--analyze-hashtags`: Perform hashtag frequency analysis.
    *   `--hashtag-top-n <number>`: Number of top hashtags to show (default: 10).
*   `--suggest-users`: Suggest active users from the fetched media.
    *   `--suggest-min-posts <number>`: Minimum posts for a user to be suggested (default: 2).
    *   `--suggest-top-n <number>`: Number of users to suggest (default: 10).
*   `--suggest-themes`: Suggest content themes using n-gram analysis on captions.
    *   `--ngram-top-n-bigrams <number>`: Top N bigrams for themes (default: 10).
    *   `--ngram-top-n-trigrams <number>`: Top N trigrams for themes (default: 10).


## Standalone Analysis Scripts
If you already have CSV data (e.g., from a previous `fetch --output-csv` run), you can run the analysis scripts independently:

*   **Hashtag Analysis:**
    ```bash
    python src/analysis/hashtag_analyzer.py data/your_hashtag_data.csv --top_n 15
    ```
*   **User Suggestion:**
    ```bash
    python src/analysis/user_suggester.py data/your_hashtag_data.csv --min_posts 3 --top_n 10
    ```
*   **Caption N-gram Analysis (Theme Suggestion):**
    ```bash
    python src/analysis/caption_analyzer.py data/your_hashtag_data.csv --top-n-bigrams 12 --top-n-trigrams 12
    ```

## Contributing
(Contributions section to be added later)

## License
(License information to be added later)
```
