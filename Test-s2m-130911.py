from doku import Doku

__author__ = 'mich'

import unittest

WIKIPATH = '/home/mich/services/sel2mers/mirror/sel2mers/wiki'

class MyTestCase(unittest.TestCase):
    def test_version(self):
        wiki = Doku(WIKIPATH)
        self.assertEqual(wiki.version, '2012-01-25 "Angua"')

    def test_load(self):
        self.assertEqual(True, False)
        wiki = Doku(WIKIPATH)
        wiki.load()
        self.assertEqual(len(wiki.root.children), 10)

if __name__ == '__main__':
    unittest.main()
