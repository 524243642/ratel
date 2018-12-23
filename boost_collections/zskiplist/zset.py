# coding: utf-8
from numpy.core.umath import isnan

from boost_collections.zskiplist.constant import ZADD_INCR, ZADD_NX, ZADD_NAN, ZADD_NOP, ZADD_UPDATED, ZADD_ADDED, OK, \
    ERR
# from boost_collections.zskiplist.zskiplist import Zskiplist
from boost_collections.zskiplist.zskiplist_ex import ZskiplistEx


class Zset(object):

    def __init__(self):
        super(Zset, self).__init__()
        self.dict_ = dict()
        # self.zsl = Zskiplist()
        self.zsl = ZskiplistEx()

    def zset_add(self, score, ele, flags):
        """
        Add a new element or update the score of an existing element in a sorted
        set.
 
        The set of flags change the command behavior. They are passed with an integer
        and will return other flags to indicate different conditions.

        The input flags are the following:

        ZADD_INCR: Increment the current element score by 'score' instead of updating
                 the current element score. If the element does not exist, we
                 assume 0 as previous score.
        ZADD_NX:   Perform the operation only if the element does not exist.

        When ZADD_INCR is used, the new score of the element is returned with result.

        The returned flags are the following:

        ZADD_NAN:     The resulting score is not a number.
        ZADD_ADDED:   The element was added (not present before the call).
        ZADD_UPDATED: The element score was updated.
        ZADD_NOP:     No operation was performed because of NX.

        Return value:

        The function returns 1 on success, and sets the appropriate flags
        ADDED or UPDATED to signal what happened during the operation (note that
        none could be set if we re-added an element using the same score it used
        to have, or in the case a zero increment is used).

        The function returns 0 on erorr, currently only when the increment
        produces a NAN condition, or when the 'score' value is NAN since the
        start.
        :param score:
        :param ele:
        :param flags:
        :return:
        """
        incr = (flags & ZADD_INCR) != 0
        nx = (flags & ZADD_NX) != 0

        if isnan(score):
            return 0, ZADD_NAN, 0
        dict_ = self.dict_
        de = dict_.get(ele, None)
        if de is not None:
            if nx:
                return 1, ZADD_NOP, 0
            curscore = de
            if incr:
                score += curscore
                if isnan(score):
                    return 0, ZADD_NAN, 0
            # Remove and re-insert when score changes.
            if score != curscore:
                result = self.zsl.zsl_delete(score=curscore, ele=ele)
                assert result == 1
                result = self.zsl.zsl_insert(score=score, ele=ele)
                assert result == 1
                dict_[ele] = score

            return 1, ZADD_UPDATED, score
        else:
            result = self.zsl.zsl_insert(score=score, ele=ele)
            assert result == 1
            assert dict_.setdefault(ele, score) == score
            return 1, ZADD_ADDED, score

    def zset_del(self, ele):
        """
        Delete the element 'ele' from the sorted set, returning 1 if the element
        existed and was deleted, 0 otherwise (the element was not there).
        :param ele:
        :return:
        """
        de = self.dict_.pop(ele, None)
        if de is not None:
            result = self.zsl.zsl_delete(score=de, ele=ele)
            assert result == 1
            return 1
        return 0

    def zset_length(self):
        """
        Return the length of the sorted set
        :return:
        """
        length = self.zsl.zsl_length()
        return length

    def zset_score(self, member):
        """
        Return (by reference) the score of the specified member of the sorted set.
        If the element does not exist ERR is returned
        otherwise OK and score is returned.
        If 'member' is NULL, ERR is returned.
        :param member:
        :return:
        """
        if member is None:
            return ERR, 0
        de = self.dict_.get(member, None)
        if de is None:
            return ERR, 0
        return OK, de

    def zset_get_floor_element_by_score(self, score):
        """
        Returns a key-value mapping associated with the greatest key
        less than or equal to the given key,or None if there is no such key.
        :param score:
        :return:
        """
        return self.zsl.zsl_get_floor_element_by_score(score)

    def zset_get_lower_element_by_score(self, score):
        """
        Returns a key-value mapping associated with the greatest key
        less than the given key,or None if there is no such key.
        :param score:
        :return:
        """
        return self.zsl.zsl_get_lower_element_by_score(score)
