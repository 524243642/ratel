# coding: utf-8
from numpy.core.umath import isnan

from boost_collections.zskiplist.constant import ZSKIPLIST_MAXLEVEL
from boost_collections.zskiplist.util import elecmp, zsl_random_level
from boost_collections.zskiplist.zskiplist_node import ZskiplistNode


class Zskiplist(object):

    def __init__(self):
        super(Zskiplist, self).__init__()
        self.header = ZskiplistNode(ZSKIPLIST_MAXLEVEL, 0)
        for j in range(0, ZSKIPLIST_MAXLEVEL):
            self.header.level[j].forward = None
            self.header.level[j].span = 0
        self.header.backward = None
        self.tail = None
        self.length = 0
        self.level = 1

    def zsl_insert(self, score, ele):
        """
        Insert a new node in the skiplist. Assumes the element does not already
        exist (up to the caller to enforce that). The skiplist takes ownership
        of the passed string 'ele'.
        :param score:
        :param ele:
        :return:
        """
        update = [None] * ZSKIPLIST_MAXLEVEL
        rank = [0] * ZSKIPLIST_MAXLEVEL

        assert (not isnan(score)), 'score can not be NaN'
        x = self.header

        i = self.level - 1
        while i >= 0:
            rank[i] = 0 if i == (self.level - 1) else rank[i + 1]
            while (x.level[i].forward and
                   (x.level[i].forward.score < score or
                    (x.level[i].forward.score == score and
                     elecmp(x.level[i].forward.ele, ele) < 0))):
                rank[i] += x.level[i].span
                x = x.level[i].forward
            update[i] = x
            i -= 1

        level = zsl_random_level()
        if level > self.level:
            for i in range(self.level, level):
                rank[i] = 0
                update[i] = self.header
                update[i].level[i].span = self.length
            self.level = level
        x = ZskiplistNode(level=level, score=score, ele=ele)
        for i in range(0, level):
            x.level[i].forward = update[i].level[i].forward
            update[i].level[i].forward = x
            x.level[i].span = update[i].level[i].span - (rank[0] - rank[i])
            update[i].level[i].span = (rank[0] - rank[i]) + 1

        for i in range(level, self.level):
            update[i].level[i].span += 1

        x.backward = None if (update[0] is self.header) else update[0]

        if x.level[0].forward:
            x.level[0].forward.backward = x
        else:
            self.tail = x
        self.length += 1
        return x

    def zsl_delete_node(self, x, update):
        for i in range(0, self.level):
            if update[i].level[i].forward is x:
                update[i].level[i].span += x.level[i].span - 1
                update[i].level[i].forward = x.level[i].forward
            else:
                update[i].level[i].span -= 1
        if x.level[0].forward:
            x.level[0].forward.backward = x.backward
        else:
            self.tail = x.backward
        while self.level > 1 and self.header.level[self.level - 1].forward is None:
            self.level -= 1
        self.length -= 1

    def zsl_delete(self, score, ele):
        update = [None] * ZSKIPLIST_MAXLEVEL
        x = self.header
        i = self.level - 1
        while i >= 0:
            while (x.level[i].forward and
                   (x.level[i].forward.score < score or
                    (x.level[i].forward.score == score and
                     elecmp(x.level[i].forward.ele, ele) < 0))):
                x = x.level[i].forward
            update[i] = x
            i -= 1
        x = x.level[0].forward
        if x and score == x.score and elecmp(x.ele, ele) == 0:
            self.zsl_delete_node(x=x, update=update)
            return 1, x
        return 0, None

    def zsl_get_element_by_rank(self, rank):
        """
        Finds an element by its rank. The rank argument needs to be 1-based.
        :param rank:
        :return:
        """
        traversed = 0
        x = self.header
        i = self.level - 1
        while i >= 0:
            while x.level[i].forward and (traversed + x.level[i].span) <= rank:
                traversed += x.level[i].span
                x = x.level[i].forward
            if traversed == rank:
                return x
            i -= 1
        return None
