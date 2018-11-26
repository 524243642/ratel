# coding: utf-8


class ZsetNode(object):

    def __init__(self, ele, score):
        super(ZsetNode, self).__init__()
        self.ele = ele
        self.score = score
