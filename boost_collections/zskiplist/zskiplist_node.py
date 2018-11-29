# coding: utf-8

from boost_collections.zskiplist.zskiplist_level import ZskiplistLevel


class ZskiplistNode(object):

    def __init__(self, level, score, ele=None):
        super(ZskiplistNode, self).__init__()
        self.ele = ele
        self.score = score
        self.backward = None
        self.level = [ZskiplistLevel() for _ in range(0, level)]
