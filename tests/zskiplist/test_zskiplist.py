import unittest

from boost_collections.zskiplist.zskiplist import Zskiplist


class TestZskiplist(unittest.TestCase):

    def setUp(self):
        self.zsl = Zskiplist()
        self.zsl.zsl_insert(10, 'a')
        self.zsl.zsl_insert(10, 'b')

    def test_zsl_insert(self):
        zsl = self.zsl
        self.zsl.zsl_insert(10, 'c')
        self.assertEqual(3, zsl.length)

    def test_zsl_delete(self):
        zsl = self.zsl
        zsl.zsl_delete(10, 'b')
        self.assertEqual(1, zsl.length)

    def test_zsl_get_element_by_rank(self):
        zsl = self.zsl
        zsl.zsl_insert(3, 'c')
        ele = zsl.zsl_get_element_by_rank(1)

        self.assertIsNotNone(ele)
        self.assertEqual('c', ele.ele)


if __name__ == '__main__':
    unittest.main()
