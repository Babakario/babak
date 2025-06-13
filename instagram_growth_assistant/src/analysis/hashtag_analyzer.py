import csv
import re
from collections import Counter
import argparse
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

HASHTAG_REGEX = re.compile(r"#(\w+)")

def extract_hashtags_from_text(text: str) -> list[str]:
    if not isinstance(text, str):
        return []
    return HASHTAG_REGEX.findall(text.lower())

def analyze_hashtag_csv(filepath: str, top_n: int = 10) -> Counter | None:
    if not os.path.exists(filepath):
        logger.error(f"CSV file not found: {filepath}")
        return None

    all_hashtags = []
    try:
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if 'caption' not in reader.fieldnames:
                logger.error(f"'caption' column not found in {filepath}. Available columns: {reader.fieldnames}")
                return None

            for row in reader:
                caption = row.get('caption', '')
                if caption:
                    hashtags_in_caption = extract_hashtags_from_text(caption)
                    all_hashtags.extend(hashtags_in_caption)
    except FileNotFoundError:
        logger.error(f"File not found during analysis: {filepath}")
        return None
    except Exception as e:
        logger.error(f"Error reading or processing CSV file {filepath}: {e}")
        return None

    if not all_hashtags:
        logger.info(f"No hashtags found in the captions in {filepath}.")
        return Counter()

    return Counter(all_hashtags)

def main():
    parser = argparse.ArgumentParser(description="Analyzes hashtags from an Instagram media CSV file.")
    parser.add_argument("csv_filepath", type=str, help="Path to the CSV file containing Instagram media data.")
    parser.add_argument("--top_n", type=int, default=10, help="Number of most common hashtags to display.")

    args = parser.parse_args()

    if not os.path.isfile(args.csv_filepath):
        logger.error(f"The file '{args.csv_filepath}' does not exist or is not a file.")
        return

    logger.info(f"Analyzing hashtags from: {args.csv_filepath}")
    counts = analyze_hashtag_csv(args.csv_filepath, args.top_n)

    if counts is not None:
        if not counts:
            print("No hashtags were found to analyze.")
        else:
            print(f"
Top {min(args.top_n, len(counts))} most common hashtags:")
            for hashtag, count in counts.most_common(args.top_n):
                print(f"  #{hashtag}: {count}")
    else:
        print("Hashtag analysis could not be completed. Check logs for errors.")

if __name__ == "__main__":
    main()
