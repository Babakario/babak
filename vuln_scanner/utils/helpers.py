from urllib.parse import urlparse

def is_valid_url(url_string: str) -> bool:
    """
    Checks if the provided string is a valid URL.
    A URL is considered valid if it has a scheme (e.g., http, https)
    and a network location (e.g., example.com).
    """
    if not isinstance(url_string, str):
        return False
    try:
        result = urlparse(url_string)
        # Ensure scheme is http or https, and netloc exists
        return result.scheme in ['http', 'https'] and all([result.netloc])
    except ValueError:
        return False
