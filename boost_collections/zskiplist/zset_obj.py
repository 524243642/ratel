# coding: utf-8
from sys import maxsize

from boost_collections.zskiplist.constant import ZADD_NX, ZADD_INCR, ZADD_ADDED, ZADD_UPDATED, ZADD_NOP, ZADD_NONE, OK
from boost_collections.zskiplist.exception import NotSupportException
from boost_collections.zskiplist.zset import Zset
from boost_collections.zskiplist.zset_node import ZsetNode


class ZsetObj(object):

    def __init__(self):
        super(ZsetObj, self).__init__()
        self.zset = Zset()

    def zrange_generic_by_score(self, reverse, min_, minex, max_, maxex, limit, withscores):
        """
        :param reverse:
        :param min_:
        :param minex:
        :param max_:
        :param maxex:
        :param limit:
        :param withscores:
        :return:
        """
        zsl = self.zset.zsl
        rets = zsl.zsl_range_generic_by_score(reverse=reverse, min_=min_, minex=minex, max_=max_, maxex=maxex,
                                              limit=limit)
        result = []
        for ret in rets:
            result.append(ZsetNode(ele=ret[0], score=ret[1] if withscores else None))
        return result

    def zrange_generic(self, reverse, start, end, withscores):
        """
        :param reverse:
        :param start:
        :param end:
        :param withscores:
        :return:
        """
        assert (-maxsize - 1) <= start <= maxsize

        llen = self.zset.zset_length()
        if start < 0:
            start = llen + start
        if end < 0:
            end = llen + end
        if start < 0:
            start = 0
        if start > end or start >= llen:
            return None
        if end >= llen:
            end = llen - 1
        rangelen = (end - start) + 1
        zsl = self.zset.zsl

        rets = zsl.zsl_range_generic(reverse=reverse, start=start, rangelen=rangelen)
        result = []
        for ret in rets:
            result.append(ZsetNode(ele=ret[0], score=ret[1] if withscores else None))
        return result

        # if reverse:
        #     ln = zsl.tail
        #     if start > 0:
        #         ln = zsl.zsl_get_element_by_rank(rank=llen - start)
        # else:
        #     ln = zsl.header.level[0].forward
        #     if start > 0:
        #         ln = zsl.zsl_get_element_by_rank(rank=start + 1)
        # result = []
        # while rangelen > 0:
        #     assert ln is not None
        #     node = ZsetNode(ele=ln.ele, score=ln.score if withscores else None)
        #     result.append(node)
        #     ln = ln.backward if reverse else ln.level[0].forward
        #     rangelen -= 1
        # return result

    def zrange_by_score(self, min_, minex, max_, maxex, limit=-1, withscores=1):
        """
        :param min_:
        :param minex:
        :param max_:
        :param maxex:
        :param limit:
        :param withscores:
        :return:
        """
        return self.zrange_generic_by_score(reverse=0, min_=min_, minex=minex, max_=max_, maxex=maxex, limit=limit,
                                            withscores=withscores)

    def zrevrange_by_score(self, min_, minex, max_, maxex, limit=-1, withscores=1):
        """
        :param min_:
        :param minex:
        :param max_:
        :param maxex:
        :param limit:
        :param withscores:
        :return:
        """
        return self.zrange_generic_by_score(reverse=1, min_=min_, minex=minex, max_=max_, maxex=maxex, limit=limit,
                                            withscores=withscores)

    def zrange(self, start, end, withscores):
        """
        :param start:
        :param end:
        :param withscores:
        :return:
        """
        return self.zrange_generic(reverse=0, start=start, end=end, withscores=withscores)

    def zrevrange(self, start, end, withscores):
        """
        :param start:
        :param end:
        :param withscores:
        :return:
        """
        return self.zrange_generic(reverse=1, start=start, end=end, withscores=withscores)

    def strcasecmp(self, s1, s2):
        if s1 is None and s2 is None:
            return True
        if s1 is None or s2 is None:
            return False
        if s1.lower() == s2.lower():
            return True
        return False

    def zadd_generic(self, flags, elements, *opts):
        """
        :param flags:
        :param elements:
        :param opts:
        :return:
        """
        added = 0
        updated = 0
        processed = 0

        assert elements is not None and len(elements) > 0

        for opt in opts:
            if self.strcasecmp(opt, "nx"):
                flags |= ZADD_NX
            elif self.strcasecmp(opt, "incr"):
                flags |= ZADD_INCR
            else:
                break

        incr = (flags & ZADD_INCR) != 0

        if incr and len(elements) > 1:
            raise NotSupportException('INCR option supports a single increment-element pair')

        for element in elements:
            retval, retflags, retscore = self.zset.zset_add(score=element.score, ele=element.ele, flags=flags)
            assert retval != 0
            if retflags & ZADD_ADDED:
                added += 1
            if retflags & ZADD_UPDATED:
                updated += 1
            if not (retflags & ZADD_NOP):
                processed += 1
            score = retscore
            element.score = score
        return added + updated

    def zadd(self, elements, *opt):
        """
        :param elements:
        :param opt:
        :return:
        """
        if not isinstance(elements, list):
            elements = [elements]
        self.zadd_generic(ZADD_NONE, elements, *opt)

    def zincrby(self, elements, *opt):
        """
        :param elements:
        :param opt:
        :return:
        """
        if not isinstance(elements, list):
            elements = [elements]
        self.zadd_generic(ZADD_INCR, elements, *opt)

    def zrem(self, *eles):
        """
        :param eles:
        :return:
        """
        deleted = 0
        for ele in eles:
            retval = self.zset.zset_del(ele=ele)
            if retval:
                deleted += 1
        return deleted

    def zcard(self):
        """
        :return:
        """
        return self.zset.zset_length()

    def zscore(self, ele):
        """
        :param ele:
        :return:
        """
        retval, retscore = self.zset.zset_score(member=ele)
        if retval == OK:
            return retscore
        return None

    def zfloor(self, score):
        """
        :param score:
        :return:
        """
        ret = self.zset.zset_get_floor_element_by_score(score=score)
        if not ret:
            return None
        return ZsetNode(ele=ret[0], score=ret[1])

    def zlower(self, score):
        """
        :param score:
        :return:
        """
        ret = self.zset.zset_get_lower_element_by_score(score=score)
        if not ret:
            return None
        return ZsetNode(ele=ret[0], score=ret[1])
