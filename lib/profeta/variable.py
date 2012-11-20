#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
variable.py
"""

import types


class Variable(object):

    Engine = None

    def __repr__ (self):

        if self.is_bound():
            return "%s(%s)" % (self.__name, self.get())
        else:
            return "%s<<undef>>" % (self.__name)

    def __init__ (self, uVarName):
        self.__name = uVarName

    def get_name (self):
        return self.__name

    def is_bound (self):
        return Variable.Engine.has_context_var(self.__name)

    def is_unbound (self):
        return not Variable.Engine.has_context_var(self.__name)

    def get(self):
        return Variable.Engine.get_context_var(self.__name)

    def set(self, uValue):
        Variable.Engine.set_context_var(self.__name, uValue)

    def match (self, uVariable):
        if (self.__name == "_") or (uVariable.get_name () == "_"):
            return True
        return self.get () == uVariable.get ()

    def match_value (self, uValue):
        if self.__name == "_":
            return True
        else:
            return self.get () == uValue

    def __getitem__(self,index):
        if self.is_bound():
            return self.get()[index]
        else:
            return self

def _(Var):
    return Variable(Var)

def v(Var):
    return Variable(Var)

def var_value(Var):
    return Variable.Engine.get_context_var (Var)

def make_terms(term_list):
    r = []
    for t in term_list:
        v = t
        if type(t) == types.StringType:
            if len(t) > 0:
                if (t[0] >= 'A') and (t[0] <= 'Z'):
                    v = Variable(t)
        r.append (v)
    return r
