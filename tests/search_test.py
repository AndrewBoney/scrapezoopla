import unittest
from scrapezoopla.scrape import search_zoopla
from bs4 import BeautifulSoup

search = search_zoopla("bristol")

class TestSearch(unittest.TestCase):
    def test_type(self):
        self.assertTrue(isinstance(search, BeautifulSoup))

# this is recommended in docs but tests break when I use. I don't really understand __main__ but potentially it
# refers to dir name?  
# if __name__ == '__main__':
#     unittest.main()