import unittest

from numpy import NaN

from boost_collections.zskiplist.exception import NotSupportException
from boost_collections.zskiplist.zset_node import ZsetNode
from boost_collections.zskiplist.zset_obj import ZsetObj


class TestZsetObj(unittest.TestCase):

    def setUp(self):
        self.zset_obj = ZsetObj()
        elements = [ZsetNode('a', 1), ZsetNode('b', 3), ZsetNode('c', 2)]
        self.zset_obj.zadd(elements=elements)

    def test_zadd(self):
        zset_obj = self.zset_obj
        zset_obj.zadd(elements=ZsetNode('d', 1))
        self.assertEqual(4, zset_obj.zcard())
        zset_obj.zadd(ZsetNode('d', 1), 'nx', None, 'ignore')
        self.assertEqual(4, zset_obj.zcard())
        zset_obj.zadd(ZsetNode('e', 2), 'nx')
        self.assertEqual(5, zset_obj.zcard())

        self.assertRaises(AssertionError, zset_obj.zadd, ZsetNode('e', NaN))

        zset_obj = ZsetObj()
        zset_obj.zadd(ZsetNode('a', 0))

    def test_zrem(self):
        zset_obj = self.zset_obj
        zset_obj.zrem('a')
        zset_obj.zrem('b')
        self.assertEqual(1, zset_obj.zcard())
        deleted = zset_obj.zrem('d')
        self.assertEqual(0, deleted)

    def test_zincrby(self):
        zset_obj = self.zset_obj
        zset_obj.zincrby(ZsetNode('a', 1), 'incr')
        score = zset_obj.zscore('a')
        self.assertEqual(2, score)

        self.assertRaises(NotSupportException, self.zincrby_notsupported_exception)

    def zincrby_notsupported_exception(self):
        zset_obj = self.zset_obj
        elements = [ZsetNode('a', 1), ZsetNode('b', 1)]
        zset_obj.zincrby(elements, 'incr')

    def test_zcard(self):
        zset_obj = self.zset_obj
        self.assertEqual(3, zset_obj.zcard())

    def test_zscore(self):
        zset_obj = self.zset_obj
        score = zset_obj.zscore('a')
        self.assertEqual(1, score)

        retval = zset_obj.zscore('d')
        self.assertEqual(None, retval)

        retval = zset_obj.zscore(None)
        self.assertEqual(None, retval)

    def test_zrange(self):
        zset_obj = self.zset_obj
        rets = zset_obj.zrange(0, 1, True)
        self.assertEqual('a', rets[0].ele)
        self.assertEqual('c', rets[1].ele)

        rets = zset_obj.zrange(0, -1, True)
        self.assertEqual('a', rets[0].ele)
        self.assertEqual('c', rets[1].ele)
        self.assertEqual('b', rets[2].ele)

        rets = zset_obj.zrange(-5, 5, True)
        self.assertEqual(3, len(rets))

        rets = zset_obj.zrange(5, -5, True)
        self.assertEqual(None, rets)
        rets = zset_obj.zrange(1, 1, True)
        self.assertEqual('c', rets[0].ele)

    def test_zrevrange(self):
        zset_obj = self.zset_obj
        rets = zset_obj.zrevrange(0, 1, True)
        self.assertEqual('b', rets[0].ele)
        self.assertEqual('c', rets[1].ele)

        rets = zset_obj.zrevrange(-1, -1, True)
        self.assertEqual('a', rets[0].ele)


if __name__ == '__main__':
    unittest.main()
