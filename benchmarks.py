import gc
import random
import time
from contextlib import contextmanager

from boost_collections.zskiplist.zset_node import ZsetNode
from boost_collections.zskiplist.zset_obj import ZsetObj


@contextmanager
def timeit(name):
    oldgc = gc.isenabled()
    gc.disable()
    print('%s:' % name)
    t1 = time.time()
    yield
    t2 = time.time()
    if oldgc:
        gc.enable()
    print(t2 - t1)


RANDOMLONGS_E4 = [random.randint(1, 500000) for i in range(10000)]
RANDOMLONGS_E3 = [random.randint(1, 500000) for i in range(1000)]


def zadd():
    zset_obj = ZsetObj()
    with timeit('add operation of SortedSet'):
        for i in RANDOMLONGS_E4:
            zset_obj.zadd(ZsetNode(str(i), i))


def list_contains():
    with timeit('search inside list'):
        for i in RANDOMLONGS_E3:
            i in RANDOMLONGS_E4


def zscore():
    zset_obj = ZsetObj()
    for i in RANDOMLONGS_E4:
        zset_obj.zadd(ZsetNode(str(i), i))
    with timeit('search inside SortedSet'):
        for i in RANDOMLONGS_E3:
            zset_obj.zscore(str(i))


if __name__ == '__main__':
    zadd()
    list_contains()
    zscore()
