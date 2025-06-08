import unittest
import sys
import os

# Add project root to sys.path to allow importing vuln_scanner
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from vuln_scanner.utils.helpers import is_valid_url

class TestHelpers(unittest.TestCase):

    def test_is_valid_url_valid(self):
        self.assertTrue(is_valid_url("http://example.com"))
        self.assertTrue(is_valid_url("https://example.com"))
        self.assertTrue(is_valid_url("https://www.example.com/path?query=123"))
        self.assertTrue(is_valid_url("http://localhost:8000"))

    def test_is_valid_url_invalid(self):
        self.assertFalse(is_valid_url("example.com")) # Missing scheme
        self.assertFalse(is_valid_url("http://")) # Missing netloc
        self.assertFalse(is_valid_url("htp://example.com")) # Invalid scheme (though urlparse might accept it, common usage expects http/https)
        self.assertFalse(is_valid_url("just_a_string"))
        self.assertFalse(is_valid_url("")) # Empty string
        self.assertFalse(is_valid_url(None)) # None input
        self.assertFalse(is_valid_url(123)) # Integer input

    def test_is_valid_url_ftp(self):
        # urllib.parse.urlparse considers 'ftp' a valid scheme.
        # Depending on requirements, one might want to restrict this further.
        # Our current is_valid_url is restricted to http/https, so this should be False.
        self.assertFalse(is_valid_url("ftp://example.com"))

if __name__ == '__main__':
    unittest.main()
