import unittest
from scrapezoopla.scrape import search_zoopla, get_property_page, ScriptData
from bs4 import BeautifulSoup

search = search_zoopla("bristol")

class TestSearch(unittest.TestCase):
    def test_type(self):
        self.assertTrue(isinstance(search, BeautifulSoup))
