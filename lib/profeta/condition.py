#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
condition.py
"""

from profeta.inference import *

import sys
import traceback
import copy
import types

#from exception import *

__all__ = ['Condition', 'TrueCondition', 'FalseCondition']

class Condition(object):

    def __init__ (self, uOne = None, uTwo = None):
        self.__matched_conditions = None
        if uTwo is None:
            if uOne is None:
                self.__conditions = []
            else:
                self.__conditions = [uOne]
        else:
            self.__conditions = [uOne, uTwo]

    def __and__ (self, uOther):
        self.append(uOther)
        return self

    def append (self, uBel):
        self.__conditions.append (uBel)

    def insert_at_top (self, uBel):
        self.__conditions.insert (0, uBel)

    def __getitem__ (self, uIndex):
        return self.__matched_conditions [uIndex]

    def __len__ (self):
        return len (self.__matched_conditions)

    def evaluate(self):
        new_matching_beliefs = [ ( [], Engine.instance().context() ) ]
        #print Engine.instance().context()
        for condition_term in self.__conditions:
            matching_beliefs = new_matching_beliefs
            new_matching_beliefs = []
            # first scan all matching_beliefs
            for (belief_list, ctx) in matching_beliefs:
                Engine.instance().set_context (ctx) # <- why?

                # if the term is a lambda expression or a predicate,
                # execute it in the local context
                if type(condition_term) == types.FunctionType:
                    eval_globals = Engine.instance().prepare_local_eval_context()
                    eval_globals["__fun"] = condition_term
                    try:
                        fun_status = eval ("__fun()", eval_globals)
                        matching_result = fun_status
                    except:
                        print "WARNING!! Unexpected error in condition evaluation:", sys.exc_info()[0]
                        traceback.print_exc()
                        matching_result = False
                    if matching_result:
                        new_matching_beliefs.append ( (belief_list, ctx) )

                else:
                    #print "#### CONDITION TERM:", condition_term
                    bel_like = Engine.kb().beliefs_like (condition_term, ctx)
                    #print "#### BELIEFS LIKE:", bel_like
                    if bel_like is None:
                        matching_result = False
                    else:
                        matching_result = True
                        for (bel, new_ctx) in bel_like:
                            b = copy.copy (belief_list)
                            b.append (bel)
                            new_matching_beliefs.append(
                                (b, Engine.instance().context_union(ctx,
                                                                    new_ctx))
                            )

                if not(matching_result):
                    del belief_list
                    del ctx
        if len(new_matching_beliefs) == 0:
            return False
#        if len(new_matching_beliefs) != 1:
    #                raise NotUniqueCondition (repr(self))
        (beliefs, ctx) = new_matching_beliefs [0]
#        print "HHHHHHHHhh", ctx
        Engine.instance().set_context (ctx)
        self.__matched_conditions = beliefs
        #print repr(new_matching_beliefs[0][0]) + "  is True"
        return True


    def __repr__(self):
        if len(self.__conditions) is not 0:
            return self.__class__.__name__ + "(" + \
                    reduce (lambda x,y : x + " " + y,
                            map (lambda x: repr(x), self.__conditions)) + \
                    ")"
        else:
            return ""


class TrueCondition(Condition):
    """A condition that evaluate always True."""
    def __repr__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        """Used for testing purpose, f.e. when you have to compare plans."""
        if isinstance(other, TrueCondition):
            return True

    def evaluate (self):
        return True


class FalseCondition(Condition):
    """A condition that evaluate always False."""
    def __repr__(self):
        return self.__class__.__name__

    def evaluate (self):
        return False
