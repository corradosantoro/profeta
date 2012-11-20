#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
action.py
"""

import logging
import threading

from profeta.inference import *

class Action(threading.Thread):

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__ (self)
#        logging.config.fileConfig("utils/logger_config.ini")
        self._logger = logging.getLogger("engine.Action")
        self._terms = make_terms(args)
        #self._terms = []
        #for i in range (0, len(args)):
        #    self._terms.append (args [i])
        self.init()

    def __getitem__ (self, uIndex):
        return self._terms[uIndex]

    def __repr__ (self):
        if len(self._terms) is not 0:
            return self.__class__.__name__ + "(" + \
                    reduce (lambda x,y : x + " " + y,
                            map (lambda x: repr(x), self._terms)) + \
                    ")"
        else:
            return self.__class__.__name__ + "()"

    def init(self):
        pass

    def run(self):
        self.execute()

    def execute(self):
        pass

