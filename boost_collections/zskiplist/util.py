# coding: utf-8
from numpy import random

from boost_collections.zskiplist.constant import ZSKIPLIST_P, ZSKIPLIST_MAXLEVEL


def zsl_random_level():
    level = 1
    while random.rand() < ZSKIPLIST_P:
        level += 1

    return level if (level < ZSKIPLIST_MAXLEVEL) else ZSKIPLIST_MAXLEVEL


def elecmp(s1, s2):
    if s1 == s2:
        return 0
    elif s1 > s2:
        return 1
    else:
        return -1
