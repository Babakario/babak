import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from vuln_scanner.core.scanner import check_sql_injection

class TestScanner(unittest.TestCase):

    def test_check_sql_injection_no_params(self):
        url = "http://example.com/page"
        vulnerable, tested_url, findings = check_sql_injection(url)
        self.assertFalse(vulnerable)
        self.assertIn("No query parameters to test for SQLi", findings[0])

    @patch('vuln_scanner.core.scanner.requests.get')
    def test_check_sql_injection_potential_vulnerability(self, mock_get):
        # Configure the mock response for a vulnerable scenario
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "you have an error in your sql syntax near '' OR '1'='1'"
        mock_get.return_value = mock_response

        url = "http://example.com/search?query=test"
        vulnerable, tested_url, findings = check_sql_injection(url)

        self.assertTrue(vulnerable)
        self.assertIn("Potential SQLi found", findings[0])
        self.assertIn("you have an error in your sql syntax", findings[0])
        # Check that requests.get was called with the modified URL
        expected_test_url_part = "query=test%27+OR+%271%27%3D%271" # ' OR '1'='1 encoded
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn(expected_test_url_part, args[0])


    @patch('vuln_scanner.core.scanner.requests.get')
    def test_check_sql_injection_no_vulnerability(self, mock_get):
        # Configure the mock response for a non-vulnerable scenario
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "search results for test"
        mock_get.return_value = mock_response

        url = "http://example.com/search?query=test"
        vulnerable, tested_url, findings = check_sql_injection(url)

        self.assertFalse(vulnerable)
        self.assertIn("No obvious SQL error patterns detected", findings[0])
        mock_get.assert_called_once()

    def test_check_sql_injection_invalid_url_input(self):
        vulnerable, tested_url, findings = check_sql_injection(123) # Invalid type
        self.assertFalse(vulnerable)
        self.assertIn("Invalid URL input", findings[0])


if __name__ == '__main__':
    unittest.main()
