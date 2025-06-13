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
from src.analysis.user_suggester import suggest_users_from_csv # New import
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def save_media_to_csv(media_items: list, hashtag_name: str, base_data_path: str) -> str | None: # MODIFIED: Return filepath
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
        return filepath # MODIFIED: Return the filepath
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
        access_token = config.get('instagram_api', 'user_access_token')
        user_id = config.get('instagram_api', 'user_id')

        if not access_token or 'YOUR_USER_ACCESS_TOKEN_HERE' in access_token or            not user_id or 'YOUR_INSTAGRAM_USER_ID_LINKED_TO_TOKEN_HERE' in user_id:
            logger.error(f"Please update your access token and user ID in {config_path}.")
            return
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        logger.error(f"Error reading configuration from {config_path}: {e}. Ensure it's correctly formatted.")
        return
    except Exception as e:
        logger.error(f"An unexpected error occurred while reading config from {config_path}: {e}")
        return

    parser = argparse.ArgumentParser(description="Instagram Growth Assistant - Hashtag Media Fetcher & Analyzer")
    parser.add_argument("hashtag", type=str, help="The hashtag to search for (without the #).")
    parser.add_argument("--limit", type=int, default=10, help="Number of recent media items to fetch.")
    parser.add_argument("--output-csv", action='store_true', help="Save the output to a CSV file in the 'data' directory.")
    # Analysis specific arguments
    parser.add_argument("--analyze-hashtags", action='store_true', help="Analyze hashtags from the output CSV (requires --output-csv).")
    parser.add_argument("--hashtag-top-n", type=int, default=10, help="Number of top hashtags to display from analysis (default: 10).")
    parser.add_argument("--suggest-users", action='store_true', help="Suggest users based on activity in the output CSV (requires --output-csv).")
    parser.add_argument("--suggest-min-posts", type=int, default=2, help="Minimum posts for a user to be suggested (default: 2).")
    parser.add_argument("--suggest-top-n", type=int, default=10, help="Number of users to suggest (default: 10).")

    args = parser.parse_args()

    if args.analyze_hashtags and not args.output_csv:
        logger.warning("--analyze-hashtags requires --output-csv to be specified. No hashtag analysis will be performed.")
        args.analyze_hashtags = False

    if args.suggest_users and not args.output_csv: # New dependency check
        logger.warning("--suggest-users requires --output-csv to be specified. No user suggestions will be performed.")
        args.suggest_users = False


    logger.info(f"Attempting to fetch up to {args.limit} media items for hashtag: #{args.hashtag} using user ID {user_id[:5]}... (token hidden)")

    media_items = instagram_client.get_hashtag_media(args.hashtag, access_token, user_id, limit=args.limit)

    saved_csv_filepath = None # MODIFIED: Variable to store CSV path

    if media_items:
        print(f"
Successfully found {len(media_items)} media items for #{args.hashtag}:")
        for i, item in enumerate(media_items):
            print(f"
--- Item {i+1} ---")
            print(f"  ID: {item.get('id')}")
            print(f"  User: @{item.get('username', 'N/A')}")
            print(f"  Timestamp: {item.get('timestamp')}")
            caption = item.get('caption', 'N/A')
            print(f"  Caption: {caption[:100] + '...' if caption and len(caption) > 100 else caption}")
            print(f"  Likes: {item.get('like_count', 'N/A')}")
            print(f"  Comments: {item.get('comments_count', 'N/A')}")
            print(f"  Link: {item.get('permalink')}")
            print(f"  Media Type: {item.get('media_type')}")

        if args.output_csv:
            data_directory = os.path.join(project_root, 'data')
            saved_csv_filepath = save_media_to_csv(media_items, args.hashtag, data_directory) # MODIFIED: Store returned path

            if saved_csv_filepath and args.analyze_hashtags:
                print("
--- Hashtag Analysis Results ---")
                analysis_counts = analyze_hashtag_csv(saved_csv_filepath, top_n=args.hashtag_top_n)
                if analysis_counts is not None:
                    if not analysis_counts:
                        print("No hashtags were found in the CSV to analyze.")
                    else:
                        print(f"Top {min(args.hashtag_top_n, len(analysis_counts))} most common hashtags found in '{os.path.basename(saved_csv_filepath)}':")
                        for tag, count in analysis_counts.most_common(args.hashtag_top_n):
                            print(f"  #{tag}: {count}")
                else:
                    print("Hashtag analysis could not be completed based on the CSV.")
            elif args.analyze_hashtags and not saved_csv_filepath :
                 logger.warning("CSV saving failed or was not requested. Skipping hashtag analysis.")

            if args.suggest_users and saved_csv_filepath:
                print("
--- User Suggestions ---")
                user_suggestions = suggest_users_from_csv(saved_csv_filepath, min_posts=args.suggest_min_posts, top_n=args.suggest_top_n)
                if user_suggestions is not None:
                    if not user_suggestions:
                        print(f"No users met the criteria (at least {args.suggest_min_posts} posts) for suggestion from '{os.path.basename(saved_csv_filepath)}'.")
                    else:
                        print(f"Top {len(user_suggestions)} suggested users (min {args.suggest_min_posts} posts) from '{os.path.basename(saved_csv_filepath)}':")
                        for user, count in user_suggestions:
                            print(f"  @{user} (found in {count} posts)")
                else:
                    print("User suggestion analysis could not be completed based on the CSV.")
            elif args.suggest_users and not saved_csv_filepath:
                logger.warning("CSV saving may have failed or was not requested. Skipping user suggestions.")
    else:
        print(f"
No media items found for #{args.hashtag}, or an error occurred during fetching. Check logs for details.")

if __name__ == "__main__":
    main()
