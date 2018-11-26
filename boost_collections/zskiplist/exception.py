# coding: utf-8


class NotSupportException(Exception):

    def __init__(self, *args, **kwargs):
        super(NotSupportException, self).__init__(*args, **kwargs)
