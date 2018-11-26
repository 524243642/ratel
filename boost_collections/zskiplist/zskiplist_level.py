# coding: utf-8


class ZskiplistLevel(object):

    def __init__(self):
        super(ZskiplistLevel, self).__init__()
        self.forward = None
        self.span = None
