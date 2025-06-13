# Instagram Growth Assistant

This project aims to provide tools and insights to help users ethically grow their Instagram presence.

## Setup
(Initial setup instructions will be added as components are developed.)

## Features (Implemented)

*   **Instagram API Client:** Fetches recent media for a given hashtag using the Instagram Graph API.
*   **Data Storage:** Saves fetched media data (ID, username, caption, likes, comments, etc.) to a CSV file.
*   **Hashtag Analysis:**
    *   Extracts and counts hashtag occurrences from the captions in the saved CSV data.
    *   Identifies the most frequently used co-occurring hashtags.
*   **User Suggestion:**
    *   Identifies users who have posted multiple times within the collected media for a hashtag.
    *   Suggests potentially relevant users based on post frequency.

## Project Structure

```
instagram_growth_assistant/
├── config/
│   ├── config.example.ini  # Example configuration, copy to config.ini
│   └── config.ini          # Your API keys and settings (gitignored)
├── data/                   # Directory for storing output CSV files (gitignored content, dir tracked by .gitkeep)
│   └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── main.py             # Main script to fetch data and run analyses
│   ├── api/
│   │   ├── __init__.py
│   │   └── instagram_client.py # Handles Instagram API communication
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── hashtag_analyzer.py # Analyzes hashtag frequency from CSV
│   │   └── user_suggester.py   # Suggests users based on CSV data
│   └── core/               # (Placeholder for future core logic)
│       └── __init__.py
├── tests/                  # Unit and integration tests
│   ├── __init__.py
│   ├── api/
│   │   └── __init__.py
│   └── analysis/
│       └── __init__.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Usage

1.  **Installation & Setup:**
    *   Clone the repository:
        ```bash
        git clone <repository_url>
        cd instagram_growth_assistant
        ```
    *   Create a virtual environment (recommended):
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        ```
    *   Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    *   **Configuration:**
        *   Copy `config/config.example.ini` to `config/config.ini`.
            ```bash
            cp config/config.example.ini config/config.ini
            ```
        *   Fill in your Instagram Graph API User Access Token and User ID in `config/config.ini`.
            **Important:** Your User Access Token must have the necessary permissions (e.g., `instagram_basic`, `instagram_manage_insights`, potentially `pages_read_engagement`, and `instagram_public_content_search` if Meta has granted this to your app after review). The User ID should be your Instagram User ID linked to the Facebook Page connected to your app. Refer to Meta's documentation for obtaining these.

2.  **Fetching Media & Saving to CSV:**
    To fetch recent media for a hashtag (e.g., "pythonprogramming") and save it to a CSV file in the `data/` directory:
    ```bash
    python src/main.py pythonprogramming --limit 20 --output-csv
    ```
    *   Replace `pythonprogramming` with your target hashtag.
    *   `--limit 20`: Fetches up to 20 posts (default is 10).
    *   `--output-csv`: Saves the fetched data to a CSV file named like `pythonprogramming_YYYYMMDD_HHMMSS.csv` in the `data/` directory.

3.  **Fetching, Saving, and Analyzing Hashtags:**
    To also analyze and display the most common hashtags found in the captions of the collected media:
    ```bash
    python src/main.py pythonprogramming --limit 20 --output-csv --analyze-hashtags --hashtag-top-n 15
    ```
    *   `--analyze-hashtags`: Performs hashtag frequency analysis on the data from the generated CSV.
    *   `--hashtag-top-n 15`: Displays the top 15 hashtags from the analysis (default is 10).

4.  **Fetching, Saving, and Suggesting Users:**
    To also get suggestions for users who are active around the target hashtag:
    ```bash
    python src/main.py naturephotography --limit 50 --output-csv --suggest-users --suggest-min-posts 3 --suggest-top-n 7
    ```
    *   `--suggest-users`: Analyzes the generated CSV to suggest users.
    *   `--suggest-min-posts 3`: Suggests users who have made at least 3 posts (default is 2).
    *   `--suggest-top-n 7`: Shows the top 7 suggested users (default is 10).

5.  **All Features Together (with custom analysis parameters):**
    ```bash
    python src/main.py artificialintelligence --limit 30 --output-csv --analyze-hashtags --hashtag-top-n 12 --suggest-users --suggest-min-posts 2 --suggest-top-n 8
    ```

6.  **Analysis Parameter Arguments (Optional):**
    When using analysis features like `--analyze-hashtags`, `--suggest-users`, or `--suggest-themes` with `src/main.py`, you can also use these optional arguments to customize the analysis:
    *   `--hashtag-top-n <number>`: Sets the number of top hashtags to show (default: 10). Used with `--analyze-hashtags`.
    *   `--suggest-min-posts <number>`: Sets the minimum number of posts a user must have to be suggested (default: 2). Used with `--suggest-users`.
    *   `--suggest-top-n <number>`: Sets the number of top users to suggest (default: 10). Used with `--suggest-users`.
    *   `--suggest-themes`: Boolean flag to enable content theme suggestions based on n-gram analysis of captions. Requires `--output-csv`.
    *   `--ngram-top-n-bigrams <number>`: Specifies the number of top common bigrams to display for theme suggestions (default: 10). Used with `--suggest-themes`.
    *   `--ngram-top-n-trigrams <number>`: Specifies the number of top common trigrams to display for theme suggestions (default: 10). Used with `--suggest-themes`.

7.  **Fetching, Saving, and Suggesting Content Themes (N-grams):**
    To analyze captions for common phrases (bigrams and trigrams) that might suggest content themes:
    ```bash
    python src/main.py foodblogger --limit 50 --output-csv --suggest-themes --ngram-top-n-bigrams 7 --ngram-top-n-trigrams 7
    ```
    *   `--suggest-themes`: Enables n-gram analysis on captions from the generated CSV.
    *   `--ngram-top-n-bigrams 7`: Displays the top 7 most common two-word phrases.
    *   `--ngram-top-n-trigrams 7`: Displays the top 7 most common three-word phrases.


8.  **All Features Together (Example Overhaul):**
    ```bash
    python src/main.py recipeideas --limit 30 --output-csv --analyze-hashtags --hashtag-top-n 8 --suggest-users --suggest-min-posts 2 --suggest-top-n 5 --suggest-themes --ngram-top-n-bigrams 5 --ngram-top-n-trigrams 5
    ```

9.  **Standalone Analysis Scripts:**
    The analysis scripts can also be run independently if you already have a CSV data file:
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
