import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Common SQL error patterns - this list can be expanded
SQL_ERROR_PATTERNS = [
    "you have an error in your sql syntax",
    "warning: mysql",
    "unclosed quotation mark after the character string",
    "quoted string not properly terminated",
    "sql syntax error",
    "pg_query()", # PostgreSQL
    "ora-01756", # Oracle
    "microsoft ole db provider for sql server", # SQL Server
    "sqlite3.error" # SQLite
]

def check_sql_injection(url: str) -> tuple[bool, str, list[str]]:
    """
    Performs a basic SQL injection check on the given URL.

    Args:
        url: The URL to test. It can include query parameters.

    Returns:
        A tuple: (vulnerable, tested_url, findings)
        vulnerable (bool): True if a potential SQLi vulnerability is detected, False otherwise.
        tested_url (str): The specific URL that triggered a detection (if any).
        findings (list[str]): List of error patterns found or messages indicating potential vulnerability.
    """
    if not isinstance(url, str):
        return False, url, ["Invalid URL input"]

    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
    except Exception as e:
        return False, url, [f"Error parsing URL: {str(e)}"]

    if not query_params:
        return False, url, ["No query parameters to test for SQLi."]

    payload = "' OR '1'='1"
    # A payload that might close a string and comment out the rest: '; --
    # payload_comment = "'; --"
    # Payloads to test: could also include payload_comment, or UNION based, etc.
    # For this basic version, we stick to one classic payload.

    vulnerable = False
    positive_tests = []
    tested_urls_details = []

    for param_name, param_values in query_params.items():
        for original_value in param_values:
            # Test with the payload appended
            modified_params = query_params.copy()
            modified_params[param_name] = [original_value + payload]

            # Reconstruct the URL with the modified query string
            modified_query_string = urlencode(modified_params, doseq=True)
            test_url = urlunparse(parsed_url._replace(query=modified_query_string))

            try:
                response = requests.get(test_url, timeout=10, allow_redirects=True)
                response_text = response.text.lower() # Compare in lowercase

                found_patterns = []
                for pattern in SQL_ERROR_PATTERNS:
                    if pattern.lower() in response_text:
                        found_patterns.append(pattern)

                if found_patterns:
                    vulnerable = True
                    details = f"Potential SQLi found at {test_url} with param '{param_name}'. Error patterns: {', '.join(found_patterns)}"
                    positive_tests.append(details)
                    tested_urls_details.append(test_url)

            except requests.exceptions.RequestException as e:
                # Could log this error, but for now, we'll just skip this test iteration
                print(f"Warning: Request failed for {test_url}: {e}")
                continue

    if vulnerable:
        # For simplicity, returning the first URL that triggered detection.
        # A more advanced version might return all problematic URLs.
        return True, tested_urls_details[0] if tested_urls_details else url, positive_tests
    else:
        return False, url, ["No obvious SQL error patterns detected in responses."]
