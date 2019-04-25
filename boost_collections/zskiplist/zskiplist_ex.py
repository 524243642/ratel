# coding: utf-8
from ._zskiplist import zskiplist


class ZskiplistEx(object):

    def __init__(self):
        super(ZskiplistEx, self).__init__()
        self._zskiplist = zskiplist()

    def zsl_insert(self, score, ele):
        return self._zskiplist.zslInsert(score, ele)

    def zsl_delete(self, score, ele):
        return self._zskiplist.zslDelete(score, ele)

    def zsl_range_generic(self, reverse, start, rangelen):
        return self._zskiplist.zslRangeGeneric(reverse, start, rangelen)

    def zsl_range_generic_by_score(self, reverse, min_, minex, max_, maxex, limit):
        return self._zskiplist.zslRangeGenericByScore(reverse, min_, minex, max_, maxex, limit)

    def zsl_get_floor_element_by_score(self, score):
        return self._zskiplist.zslGetFloorElementByScore(score)

    def zsl_get_lower_element_by_score(self, score):
        return self._zskiplist.zslGetLowerElementByScore(score)

    def zsl_length(self):
        return len(self._zskiplist)
