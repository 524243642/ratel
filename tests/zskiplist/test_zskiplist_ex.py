import unittest

from boost_collections.zskiplist.zskiplist_ex import ZskiplistEx


class TestZskiplist(unittest.TestCase):

    def setUp(self):
        self.zsl = ZskiplistEx()
        # self.zsl.zsl_insert(10, 'a')
        # self.zsl.zsl_insert(5, 'b')

    def test_zsl_length(self):
        zsl = self.zsl
        # length = zsl.zsl_length()
        # self.assertEqual(2, length)

    def test_zsl_insert(self):
        zsl = self.zsl
        result = self.zsl.zsl_insert(11, 'c')
        self.assertEqual(1, result)
        self.assertEqual(3, zsl.zsl_length())

    def test_zsl_delete(self):
        zsl = self.zsl
        result = zsl.zsl_delete(5, 'b')
        self.assertEqual(1, zsl.zsl_length())
        self.assertEqual(1, result)

    def test_zsl_range_generic(self):
        zsl = self.zsl
        self.zsl.zsl_insert(-1, 'c')
        result = zsl.zsl_range_generic(0, 0, 1)
        self.assertEqual([('c', -1.0)], result)


if __name__ == '__main__':
    unittest.main()
