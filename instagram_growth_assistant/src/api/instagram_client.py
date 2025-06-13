import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_GRAPH_URL = "https://graph.facebook.com/v18.0"

def get_hashtag_id(hashtag_name: str, access_token: str, user_id: str) -> str | None:
    '''
    Retrieves the ID of a hashtag using the Instagram Graph API.
    '''
    url = f"{BASE_GRAPH_URL}/ig_hashtag_search"
    params = {
        "user_id": user_id,
        "q": hashtag_name,
        "access_token": access_token,
    }
    response = None
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("data") and len(data["data"]) > 0:
            return data["data"][0]["id"]
        else:
            logger.warning(f"No ID found for hashtag: {hashtag_name}. Response: {data}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching hashtag ID for '{hashtag_name}': {e}")
        if response is not None:
            logger.error(f"Response status code: {response.status_code}, Response content: {response.text}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_hashtag_id for '{hashtag_name}': {e}")
        return None

def get_recent_media_by_hashtag_id(
    hashtag_id: str, access_token: str, user_id: str, limit: int = 20,
    fields: str = "id,caption,media_type,media_url,permalink,timestamp,username,like_count,comments_count"
) -> list:
    '''
    Retrieves recent media for a given hashtag ID using the Instagram Graph API.
    '''
    if not hashtag_id:
        logger.warning("No hashtag ID provided to get_recent_media_by_hashtag_id.")
        return []

    url = f"{BASE_GRAPH_URL}/{hashtag_id}/recent_media"
    params = {
        "user_id": user_id,
        "fields": fields,
        "access_token": access_token,
        "limit": min(limit, 50)
    }

    media_items = []
    response = None
    try:
        current_url = url
        page_count = 0

        while current_url and len(media_items) < limit and page_count < 5: # Max 5 pages for this basic version
            if page_count > 0 :
                response = requests.get(current_url)
            else:
                response = requests.get(current_url, params=params)

            response.raise_for_status()
            data = response.json()

            fetched_data = data.get("data", [])
            media_items.extend(fetched_data)

            if len(media_items) >= limit:
                media_items = media_items[:limit]
                break

            paging = data.get("paging", {})
            current_url = paging.get("next")
            page_count += 1
            if not current_url:
                break

        return media_items

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching media for hashtag ID '{hashtag_id}': {e}")
        if response is not None:
            logger.error(f"Response status code: {response.status_code}, Response content: {response.text}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_recent_media_by_hashtag_id for ID '{hashtag_id}': {e}")
        return []


def get_hashtag_media(hashtag_name: str, access_token: str, user_id: str, limit: int = 20) -> list:
    '''
    Fetches recent media for a given hashtag name.
    First gets the hashtag ID, then fetches media.
    '''
    logger.info(f"Fetching media for hashtag: {hashtag_name}")
    hashtag_id = get_hashtag_id(hashtag_name, access_token, user_id)
    if hashtag_id:
        logger.info(f"Found ID {hashtag_id} for hashtag '{hashtag_name}'. Fetching media...")
        return get_recent_media_by_hashtag_id(hashtag_id, access_token, user_id, limit)
    else:
        logger.warning(f"Could not retrieve media for hashtag '{hashtag_name}' as its ID was not found.")
        return []
