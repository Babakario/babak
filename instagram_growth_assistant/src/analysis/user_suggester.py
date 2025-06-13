import csv
import argparse
import os
from collections import Counter
import logging
logger = logging.getLogger(__name__)
def suggest_users_from_csv(filepath: str, min_posts: int = 2, top_n: int = 10) -> list[tuple[str, int]] | None:
    """
    Reads a CSV file, analyzes the 'username' column to find users
    who have posted at least 'min_posts' times.
    Returns a list of (username, post_count) tuples for the top_n users,
    sorted by post count (descending) and then username (ascending).
    """
    if not os.path.exists(filepath): # Use os.path.exists
        logger.error(f"CSV file not found: {filepath}")
        return None

    usernames = [] # Initialize list to store usernames

        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                if 'username' not in reader.fieldnames:
                    logger.error(f"'username' column not found in {filepath}. Available columns: {reader.fieldnames}")
                    return None # Return None if 'username' column is missing

                for row in reader:
                    username = row.get('username')
                    # Ensure username is valid and not a placeholder like 'N/A'
                    if username and username.strip() and username != 'N/A':
                        usernames.append(username)
        except FileNotFoundError: # Should be caught by os.path.exists, but good for robustness
            logger.error(f"File not found during user suggestion analysis: {filepath}")
            return None
        except Exception as e:
            logger.error(f"Error reading or processing CSV file {filepath} for user suggestions: {e}")
            return None

        if not usernames: # Check if the list of usernames (populated by CSV reader) is empty
            logger.info(f"No valid usernames found in the 'username' column in {filepath} after processing.")
            return [] # Return empty list if no usernames were actually found

        user_counts = Counter(usernames) # Use Counter

        suggested_users_candidates = []
        for user, count in user_counts.items():
            if count >= min_posts:
                suggested_users_candidates.append((user, count))

        # Sort by post count (descending) then by username (ascending) for tie-breaking
        suggested_users_candidates.sort(key=lambda x: (-x[1], x[0]))

        return suggested_users_candidates[:top_n] # Return the top_n results
def main():
    # Argument parsing setup
    parser = argparse.ArgumentParser(description="Suggests active users from an Instagram media CSV file.")
    parser.add_argument("csv_filepath", type=str, help="Path to the CSV file (must include a 'username' column).")
    parser.add_argument("--min_posts", type=int, default=2, help="Minimum number of posts for a user to be suggested.")
    parser.add_argument("--top_n", type=int, default=10, help="Maximum number of users to suggest.")

    args = parser.parse_args()

    # Check if file exists using os.path.isfile
    if not os.path.isfile(args.csv_filepath):
        logger.error(f"The file '{args.csv_filepath}' does not exist or is not a file.")
        return

    logger.info(f"Suggesting users from: {args.csv_filepath} (min posts: {args.min_posts}, top N: {args.top_n})")
    suggestions = suggest_users_from_csv(args.csv_filepath, args.min_posts, args.top_n)

    if suggestions is not None: # Check if suggestions is not None (means no major error in suggest_users_from_csv)
        if not suggestions: # Check if the list of suggestions is empty
            print(f"No users met the criteria (at least {args.min_posts} post(s) in the provided CSV).")
        else:
            print(f"
Top {len(suggestions)} suggested users (found with at least {args.min_posts} post(s) in the CSV):")
            for user, count in suggestions:
                print(f"  @{user} (found in {count} posts)")
    else:
        # This case implies an error occurred in suggest_users_from_csv, which should have been logged
        print("User suggestion analysis could not be completed. Check logs for errors.")
if __name__ == "__main__":
    main()
