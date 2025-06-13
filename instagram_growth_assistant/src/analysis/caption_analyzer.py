import csv
import re
import os
import argparse
import logging
from collections import Counter # For future use

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Basic punctuation regex (can be expanded)
PUNCTUATION_REGEX = re.compile(r'[^\w\s]') # Keep word characters and whitespace

# Simple list of English stop words (can be expanded or use a library later)
STOP_WORDS = set([
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "should", "can",
    "could", "may", "might", "must", "am", "i", "you", "he", "she", "it", "we",
    "they", "me", "my", "myself", "your", "yours", "yourself", "him", "his",
    "himself", "her", "hers", "herself", "its", "itself", "us", "our", "ours",
    "ourselves", "them", "their", "theirs", "themselves", "what", "which", "who",
    "whom", "this", "that", "these", "those", "to", "of", "at", "by", "for",
    "with", "about", "against", "between", "into", "through", "during", "before",
    "after", "above", "below", "from", "up", "down", "in", "out", "on", "off",
    "over", "under", "again", "further", "then", "once", "here", "there", "when",
    "where", "why", "how", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "s", "t", "just", "don", "shouldve", "now"
])


def extract_common_ngrams(csv_filepath: str, top_n_bigrams: int = 10, top_n_trigrams: int = 10) -> tuple[list, list] | None:
    """
    Reads 'caption' column from a CSV, processes text, and extracts common
    bigrams and trigrams.
    (Placeholder implementation)
    """
    if not os.path.exists(csv_filepath):
        logger.error(f"CSV file not found: {csv_filepath}")
        return None

    all_captions_text = []
    try:
        with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if 'caption' not in reader.fieldnames:
                logger.error(f"'caption' column not found in {csv_filepath}. Available columns: {reader.fieldnames}")
                return None
            for row in reader:
                caption = row.get('caption', '')
                if caption and caption.strip():
                    all_captions_text.append(caption)
    except FileNotFoundError:
        logger.error(f"File not found during n-gram analysis: {csv_filepath}")
        return None
    except Exception as e:
        logger.error(f"Error reading CSV {csv_filepath} for n-gram analysis: {e}")
        return None

    if not all_captions_text:
        logger.info(f"No captions found in {csv_filepath} to analyze for n-grams.")
        return [], [] # Return empty lists if no captions

    processed_words_list = []
    for text in all_captions_text:
        text = text.lower()
        text = PUNCTUATION_REGEX.sub(' ', text) # Replace punctuation with space
        words = text.split()
        # Filter out stop words and very short words (e.g., single characters if any remain)
        words = [word for word in words if word not in STOP_WORDS and len(word) > 1]
        processed_words_list.append(words) # Keep captions separate for n-gram generation per caption

    all_bigrams = []
    all_trigrams = []

    for words in processed_words_list:
        if len(words) >= 2:
            for i in range(len(words) - 1):
                all_bigrams.append((words[i], words[i+1]))
        if len(words) >= 3:
            for i in range(len(words) - 2):
                all_trigrams.append((words[i], words[i+1], words[i+2]))

    if not all_bigrams and not all_trigrams:
        logger.info("No n-grams could be generated after processing captions (e.g., all captions were too short or only contained stop words).")
        return [], []

    bigram_counts = Counter(all_bigrams)
    trigram_counts = Counter(all_trigrams)

    common_bigrams = bigram_counts.most_common(top_n_bigrams)
    common_trigrams = trigram_counts.most_common(top_n_trigrams)

    return common_bigrams, common_trigrams

def main():
    parser = argparse.ArgumentParser(description="Analyzes n-grams (common phrases) from Instagram media captions in a CSV file.")
    parser.add_argument("csv_filepath", type=str, help="Path to the CSV file (must include a 'caption' column).")
    parser.add_argument("--top-n-bigrams", type=int, default=10, help="Number of most common bigrams to display.")
    parser.add_argument("--top-n-trigrams", type=int, default=10, help="Number of most common trigrams to display.")

    args = parser.parse_args()

    if not os.path.isfile(args.csv_filepath):
        logger.error(f"The file '{args.csv_filepath}' does not exist or is not a file.")
        return

    logger.info(f"Starting n-gram analysis for: {args.csv_filepath}")
    results = extract_common_ngrams(args.csv_filepath, args.top_n_bigrams, args.top_n_trigrams)

    if results:
        common_bigrams, common_trigrams = results
        print(f"
Top {len(common_bigrams)} Common Bigrams:")
        if common_bigrams:
            for bigram, count in common_bigrams:
                print(f"  '{' '.join(bigram)}': {count}")
        else:
            print("  No bigrams found or criteria not met.")

        print(f"
Top {len(common_trigrams)} Common Trigrams:")
        if common_trigrams:
            for trigram, count in common_trigrams:
                print(f"  '{' '.join(trigram)}': {count}")
        else:
            print("  No trigrams found or criteria not met.")
    else:
        print("N-gram analysis could not be completed. Check logs for errors.")

if __name__ == "__main__":
    main()
