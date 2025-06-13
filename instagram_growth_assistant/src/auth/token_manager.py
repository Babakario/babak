import json
import os
import logging

logger = logging.getLogger(__name__)

DEFAULT_TOKEN_CACHE_PATH = ".instagram_token_cache.json" # At the project root

def save_access_token(token_data: dict, filepath: str = DEFAULT_TOKEN_CACHE_PATH):
    """Saves access token data to a JSON file."""
    if not isinstance(token_data, dict):
        logger.error("Invalid token_data provided. Must be a dictionary.")
        return False

    try:
        # Ensure the directory for the filepath exists if it's not in root
        # For DEFAULT_TOKEN_CACHE_PATH, this is not strictly necessary but good practice if path was deeper
        # base_dir = os.path.dirname(filepath)
        # if base_dir and not os.path.exists(base_dir):
        #     os.makedirs(base_dir, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(token_data, f, indent=4)
        logger.info(f"Access token saved successfully to {filepath}")
        return True
    except IOError as e:
        logger.error(f"Error saving access token to {filepath}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while saving token: {e}")
    return False

def load_access_token(filepath: str = DEFAULT_TOKEN_CACHE_PATH) -> dict | None:
    """Loads access token data from a JSON file."""
    if not os.path.exists(filepath):
        logger.debug(f"Token cache file not found at {filepath}. No token loaded.")
        return None

    try:
        with open(filepath, 'r') as f:
            token_data = json.load(f)
        if isinstance(token_data, dict) and "access_token" in token_data: # Basic validation
            logger.info(f"Access token loaded successfully from {filepath}")
            return token_data
        else:
            logger.warning(f"Invalid or corrupted token data in {filepath}.")
            # Optionally, delete corrupted file: os.remove(filepath)
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from token file {filepath}: {e}")
    except IOError as e:
        logger.error(f"Error loading access token from {filepath}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading token: {e}")
    return None

def delete_access_token(filepath: str = DEFAULT_TOKEN_CACHE_PATH) -> bool:
    """Deletes the access token cache file."""
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            logger.info(f"Access token cache file {filepath} deleted successfully (logout).")
            return True
        except OSError as e:
            logger.error(f"Error deleting token cache file {filepath}: {e}")
            return False
    else:
        logger.info(f"No token cache file found at {filepath} to delete.")
        return True # Idempotent: if it's not there, it's effectively 'deleted'

# Example usage (for testing this module directly, if needed)
if __name__ == '__main__':
    print("Testing token_manager.py functions...")
    test_token = {"access_token": "sample_test_token_12345", "user_id": "test_user"}

    # Test save
    print(f"Saving token: {test_token}")
    save_success = save_access_token(test_token, ".test_cache.json")
    print(f"Save successful: {save_success}")

    # Test load
    print("Loading token...")
    loaded_token = load_access_token(".test_cache.json")
    if loaded_token:
        print(f"Loaded token: {loaded_token}")
        assert loaded_token == test_token
    else:
        print("Failed to load token or token not found.")

    # Test delete
    print("Deleting token...")
    delete_success = delete_access_token(".test_cache.json")
    print(f"Delete successful: {delete_success}")

    # Verify deletion by trying to load again
    print("Attempting to load deleted token...")
    loaded_after_delete = load_access_token(".test_cache.json")
    if loaded_after_delete is None:
        print("Token successfully verified as deleted.")
    else:
        print(f"ERROR: Token still exists after deletion: {loaded_after_delete}")
