# Ratel

[![PyPI version](https://badge.fury.io/py/ratel.svg)](https://badge.fury.io/py/ratel)
[![Build Status](https://travis-ci.org/524243642/ratel.svg?branch=master)](https://travis-ci.org/524243642/ratel)
[![codecov](https://codecov.io/gh/524243642/ratel/branch/master/graph/badge.svg)](https://codecov.io/gh/524243642/ratel)

Skip list is a data structure that allows fast search within an ordered sequence 
of elements and a probabilistic alternative to Balanced Trees.It is also easier
to implement.
This library uses redis skip list to implement SortedSet data types for Python

This library modified in three ways:
1) This implementation is allowed to repeated scores.
2) The comparison is not just by score but by key data.
3) It's a doubly linked list with the backward being only at "level 1". 
   This allows to traverse the list from tail to head, useful for zrevrange.
4) This implementation is combined with dict data structure for fast search.

Skip Lists are data structure that can be used in place of balanced trees. They
are easier to implement and generally faster. This library uses redis skip lists to
implement SortedSet data types for Python.

SortedSet is implemented in Python and C with high performance.

Here is a few examples:
```python
from boost_collections.zskiplist.zset_node import ZsetNode
from boost_collections.zskiplist.zset_obj import ZsetObj
zset_obj = ZsetObj()
elements = [ZsetNode('a', 1), ZsetNode('a', 2), ZsetNode('c', 2)]
# multi elements added
zset_obj.zadd(elements=elements)
# multi elements added nx
zset_obj.zadd(elements=elements, 'nx')
# one element added
zset_obj.zadd(elements=ZsetNode('d', 1))
# zincrby
zset_obj.zincrby(ZsetNode('a', 1), 'incr')
# zcard
zset_obj.zcard()
# zscore
zset_obj.zscore('a')
# zrange
zset_obj.zrange(0, -1, True)
# zrevrange
zset_obj.zrevrange(0, 1, True)
```
# Compatibility
* Python 2.7, 3.5+

# Installation
```
pip install ratel
```
or
```
https://github.com/524243642/ratel
cd ratel
python setup.py install
```


# Time Complexity
ZsetObj Operations   | Average Case
-------------------- | ------------
zadd                 | O(log N)
zincrby              | O(log N)
zrem                 | O(log N)
zscore               | O(1)
zcard                | O(1)
zrange               | O(log N)
zrevrange            | O(log N)

# License
MIT

# Contributing
Welcome to feedback and improvements.Please submit a pull request!