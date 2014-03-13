# -*- coding: utf-8 -*-
import unittest
from wikipedia_searcher.wikipedia_searcher import WikipediaSearcher

class TestWikipediaSearcher(unittest.TestCase):
    def setUp(self):
        self.searcher = WikipediaSearcher()

    def test_full_text_english(self):
        result = self.searcher.simple_entry_search('kusareru', action='full')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], u'http://en.wikipedia.org/wiki/List_of_jōyō_kanji')

    def test_full_text_unicode(self):
        result = self.searcher.simple_entry_search(u'アスクライブ', action='full', language='ja')
        self.assertEqual(len(result), 3)

    def test_full_text_unicode_query_continue(self):
        result = self.searcher.simple_entry_search(u'生きていたい', action='full', language='ja')
        self.assertEqual(len(result), 19)

    def test_exact(self):
        result = self.searcher.simple_entry_search(u'Toyotomi Hideyoshi',language='en')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], u'<http://en.wikipedia.org/wiki/Toyotomi_Hideyoshi>')
        self.assertEqual(result[0][1], u'"Toyotomi Hideyoshi"@en')
        self.assertEqual(result[0][3], u'')

    def test_exact_redirect(self):
        result = self.searcher.simple_entry_search(u'Masuko',language='en')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], u'<http://en.wikipedia.org/wiki/Masuko>')
        self.assertEqual(result[0][1], u'"Masuko"@en')
        self.assertEqual(result[0][2], u'')
        self.assertEqual(result[0][3], u'"Aitarō Masuko"@en')

    def test_exact_unicode(self):
        result = self.searcher.simple_entry_search(u'明治神宮', language='ja', action='exact')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], u'<http://ja.wikipedia.org/wiki/明治神宮>')
        self.assertEqual(result[0][1], u'"明治神宮"@ja')
        self.assertEqual(result[0][3], u'')

    def test_forward(self):
        result = self.searcher.simple_entry_search(u'Hideyoshi', language='en', action='forward')
        self.assertEqual(len(result), 14)

    def test_forward_unicode(self):
        result = self.searcher.simple_entry_search(u'プログラミング', language='ja', action='forward')
        self.assertGreater(len(result), 1)

    def test_invalid_action_name(self):
        args = {
            'word':u'Hideyoshi',
            'language':'en',
            'action':'invalid_action'
        }
        self.assertRaises(ValueError, self.searcher.simple_entry_search, **args)

if __name__ == '__main__':
    unittest.main()
