import argparse
import configparser
import os
import sys
import csv
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.api import instagram_client
from src.analysis.hashtag_analyzer import analyze_hashtag_csv
from src.analysis.user_suggester import suggest_users_from_csv
from src.analysis.caption_analyzer import extract_common_ngrams
from src.auth import instagram_oauth
from src.auth.token_manager import save_access_token, load_access_token, delete_access_token # New import

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def save_media_to_csv(media_items: list, hashtag_name: str, base_data_path: str) -> str | None:
    # ... (function content remains the same - omitted for brevity)
    if not media_items:
        logger.info("No media items to save.")
        return None
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{hashtag_name}_{timestamp_str}.csv"
    filepath = os.path.join(base_data_path, filename)
    os.makedirs(base_data_path, exist_ok=True)
    headers = ['id', 'username', 'timestamp', 'caption', 'like_count', 'comments_count', 'permalink', 'media_type']
    logger.info(f"Saving {len(media_items)} media items to {filepath}...")
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            for item in media_items:
                row_data = {header: item.get(header, '') for header in headers}
                writer.writerow(row_data)
        logger.info(f"Successfully saved media items to {filepath}")
        return filepath
    except IOError as e:
        logger.error(f"Error writing to CSV file {filepath}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while saving to CSV {filepath}: {e}")
    return None


def main():
    config = configparser.ConfigParser()
    config_file_name = 'config.ini'
    config_path = os.path.join(project_root, 'config', config_file_name)

    if not os.path.exists(config_path):
        example_config_path = os.path.join(project_root, 'config', 'config.example.ini')
        logger.error(f"Configuration file not found at {os.path.abspath(config_path)}.")
        logger.error(f"Please copy '{os.path.basename(example_config_path)}' to '{config_file_name}' in the '{os.path.dirname(config_path)}' directory and fill it out.")
        return

    try:
        config.read(config_path)
        user_access_token = config.get('instagram_api', 'user_access_token', fallback=None)
        user_id = config.get('instagram_api', 'user_id', fallback=None)
        app_id = config.get('instagram_app_oauth', 'app_id', fallback=None)
        app_secret = config.get('instagram_app_oauth', 'app_secret', fallback=None)
        redirect_uri = config.get('instagram_app_oauth', 'redirect_uri', fallback=None)
    except configparser.Error as e:
        logger.error(f"Error reading configuration from {config_path}: {e}.")
        return

    # --- Argument Parsing Setup with Sub-commands ---
    parser = argparse.ArgumentParser(description="Instagram Growth Assistant")
    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

    # --- 'fetch' command ---
    fetch_parser = subparsers.add_parser('fetch', help='Fetch media for a hashtag and optionally analyze/suggest.')
    fetch_parser.add_argument("hashtag", type=str, help="The hashtag to search for (without the #).")
    fetch_parser.add_argument("--limit", type=int, default=10, help="Number of recent media items to fetch.")
    fetch_parser.add_argument("--output-csv", action='store_true', help="Save the output to a CSV file in the 'data' directory.")
    fetch_parser.add_argument("--analyze-hashtags", action='store_true', help="Analyze hashtags from the output CSV (requires --output-csv).")
    fetch_parser.add_argument("--hashtag-top-n", type=int, default=10, help="Number of top hashtags to display from analysis (default: 10).")
    fetch_parser.add_argument("--suggest-users", action='store_true', help="Suggest users based on activity in the output CSV (requires --output-csv).")
    fetch_parser.add_argument("--suggest-min-posts", type=int, default=2, help="Minimum posts for a user to be suggested (default: 2).")
    fetch_parser.add_argument("--suggest-top-n", type=int, default=10, help="Number of users to suggest (default: 10).")
    fetch_parser.add_argument("--suggest-themes", action='store_true', help="Suggest content themes based on n-gram analysis of captions (requires --output-csv).")
    fetch_parser.add_argument("--ngram-top-n-bigrams", type=int, default=10, help="Number of top bigrams to suggest for themes (default: 10).")
    fetch_parser.add_argument("--ngram-top-n-trigrams", type=int, default=10, help="Number of top trigrams to suggest for themes (default: 10).")

    # --- 'instagram_login' command ---
    login_parser = subparsers.add_parser('instagram_login', help='Start the Instagram OAuth login process to get a user access token.')

    # --- 'instagram_complete_auth' command ---
    complete_auth_parser = subparsers.add_parser('instagram_complete_auth', help='Complete the Instagram OAuth process using the authorization code.')
    complete_auth_parser.add_argument('--code', type=str, required=True, help='The authorization code obtained from Instagram after redirect.')

    # --- 'instagram_logout' command ---
    logout_parser = subparsers.add_parser('instagram_logout', help='Log out by deleting the stored Instagram access token.')

    # TODO: Future commands requiring authentication (e.g., for follower analysis)
    # will need to call load_access_token() here or at their entry points.
    # If no token is found, they should guide the user to log in.
    # Example:
    # if args.command == 'analyze_my_followers': # Hypothetical
    #     loaded_user_token = load_access_token()
    #     if not loaded_user_token:
    #         logger.error("This feature requires you to be logged in. Use 'instagram_login' and 'instagram_complete_auth'.")
    #         return
    #     # Proceed with using loaded_user_token['access_token']

    args = parser.parse_args()

    # --- Command Handling ---
    if args.command == 'fetch':
        if not user_access_token or 'YOUR_USER_ACCESS_TOKEN_HERE' in user_access_token or \
           not user_id or 'YOUR_INSTAGRAM_USER_ID_LINKED_TO_TOKEN_HERE' in user_id:
            logger.error(f"Public content access token or user ID in [instagram_api] section of {config_path} is missing or uses placeholder values. These are required for the 'fetch' command. Please update them.")
            return
        if args.analyze_hashtags and not args.output_csv:
            logger.warning("--analyze-hashtags requires --output-csv. No hashtag analysis will be performed.")
            args.analyze_hashtags = False
        if args.suggest_users and not args.output_csv:
            logger.warning("--suggest-users requires --output-csv. No user suggestions will be performed.")
            args.suggest_users = False
        if args.suggest_themes and not args.output_csv:
            logger.warning("--suggest-themes requires --output-csv. No theme suggestions will be performed.")
            args.suggest_themes = False

        logger.info(f"Fetching up to {args.limit} media items for hashtag: #{args.hashtag} using user ID {user_id[:5]}... (token hidden)")
        media_items = instagram_client.get_hashtag_media(args.hashtag, user_access_token, user_id, limit=args.limit)
        saved_csv_filepath = None
        if media_items:
            print(f"\nSuccessfully found {len(media_items)} media items for #{args.hashtag}:")
            for i, item in enumerate(media_items): # Simplified print
                 print(f"  Item {i+1}: ID {item.get('id')}, User @{item.get('username','N/A')}, Caption: \"{str(item.get('caption', 'N/A'))[:30]}...\", Link {item.get('permalink')}")


            if args.output_csv:
                data_directory = os.path.join(project_root, 'data')
                saved_csv_filepath = save_media_to_csv(media_items, args.hashtag, data_directory)

            if saved_csv_filepath:
                if args.analyze_hashtags:
                    print("\n--- Hashtag Analysis Results ---")
                    analysis_counts = analyze_hashtag_csv(saved_csv_filepath, top_n=args.hashtag_top_n)
                    if analysis_counts is not None:
                        if not analysis_counts: print("No hashtags found to analyze.")
                        else:
                            print(f"Top {min(args.hashtag_top_n, len(analysis_counts))} hashtags:")
                            for tag, count in analysis_counts.most_common(args.hashtag_top_n): print(f"  #{tag}: {count}")
                    else: print("Hashtag analysis failed.")

                if args.suggest_users:
                    print("\n--- User Suggestions ---")
                    user_suggestions = suggest_users_from_csv(saved_csv_filepath, min_posts=args.suggest_min_posts, top_n=args.suggest_top_n)
                    if user_suggestions is not None:
                        if not user_suggestions: print(f"No users met criteria (min {args.suggest_min_posts} posts).")
                        else:
                            print(f"Top {len(user_suggestions)} users (min {args.suggest_min_posts} posts):")
                            for user, count in user_suggestions: print(f"  @{user} ({count} posts)")
                    else: print("User suggestion failed.")

                if args.suggest_themes:
                    print("\n--- Content Theme Suggestions (N-grams) ---")
                    ngram_results = extract_common_ngrams(saved_csv_filepath, top_n_bigrams=args.ngram_top_n_bigrams, top_n_trigrams=args.ngram_top_n_trigrams)
                    if ngram_results:
                        common_bigrams, common_trigrams = ngram_results
                        print(f"Top {len(common_bigrams)} Bigrams:")
                        if common_bigrams:
                            for bigram, count in common_bigrams: print(f"  '{' '.join(bigram)}': {count}")
                        else: print("  No significant bigrams.")
                        print(f"\nTop {len(common_trigrams)} Trigrams:")
                        if common_trigrams:
                            for trigram, count in common_trigrams: print(f"  '{' '.join(trigram)}': {count}")
                        else: print("  No significant trigrams.")
                    else: print("N-gram analysis failed.")
            elif (args.analyze_hashtags or args.suggest_users or args.suggest_themes):
                 logger.warning("CSV output was not enabled or failed, so analyses depending on it were skipped.")
        else:
            print(f"\nNo media items found for #{args.hashtag}, or an error occurred during fetching.")

    elif args.command == 'instagram_login':
        if not app_id or 'YOUR_INSTAGRAM_APP_ID_HERE' in app_id or \
           not redirect_uri or 'YOUR_CONFIGURED_REDIRECT_URI_HERE' in redirect_uri:
            logger.error(f"Instagram App ID or Redirect URI is missing or uses placeholder values in [instagram_app_oauth] section of {config_path}. These are required for the 'instagram_login' command.")
            return

        scopes = instagram_oauth.DEFAULT_SCOPES
        auth_url = instagram_oauth.generate_authorization_url(app_id, redirect_uri, scope=scopes)
        print("\n--- Instagram OAuth Login ---")
        print("Please open the following URL in your browser to authorize the application:")
        print(f"\n{auth_url}\n")
        print("After authorization, Instagram will redirect you to your configured redirect_uri.")
        print("Copy the 'code' parameter from the URL in your browser's address bar.")
        print("Then, run the following command:")
        print(f"  python src/main.py instagram_complete_auth --code YOUR_COPIED_CODE_HERE")

    elif args.command == 'instagram_complete_auth':
        if not app_id or 'YOUR_INSTAGRAM_APP_ID_HERE' in app_id or \
           not app_secret or 'YOUR_INSTAGRAM_APP_SECRET_HERE' in app_secret or \
           not redirect_uri or 'YOUR_CONFIGURED_REDIRECT_URI_HERE' in redirect_uri:
            logger.error(f"Instagram App ID, App Secret, or Redirect URI is missing or uses placeholder values in [instagram_app_oauth] section of {config_path}. These are required for the 'instagram_complete_auth' command.")
            return

        auth_code = args.code
        print(f"\n--- Completing Instagram OAuth ---")
        print(f"Attempting to exchange authorization code '{auth_code[:20]}...' for an access token...")

        token_data = instagram_oauth.exchange_code_for_access_token(app_id, app_secret, redirect_uri, auth_code)

        if token_data:
            print("\nAuthentication successful! (Placeholder token data below)")
            print(f"User ID: {token_data.get('user_id')}")
            print(f"Short-lived Access Token: {token_data.get('access_token')}")

            save_success = save_access_token(token_data) # Using default filepath
            if save_success:
                print("Access token saved successfully.")
                logger.info("Token data also contains user_id. Consider exchanging for a long-lived token next.")
            else:
                print("Failed to save access token. Please check logs.")
        else:
            print("\nAuthentication failed. Could not exchange code for token.")
            logger.error("Token exchange failed. Check previous logs from instagram_oauth module for details if any.")

    elif args.command == 'instagram_logout':
        print("\n--- Instagram Logout ---")
        deleted = delete_access_token() # Using default filepath
        if deleted:
            print("Logged out successfully. Token cache file deleted (if it existed).")
        else:
            print("Error occurred during logout. Check logs.")


if __name__ == "__main__":
    main()
