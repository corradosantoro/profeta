#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
exception.py
"""


class BeliefEventTypeNotDefined(Exception):
    """Belief event has to be `add or `delete"""

class GoalEventTypeNotDefined(Exception):
    """Goal event has to be `add or `delete"""

class NotGroundBelief(Exception):
    """Passed belief has some free variables"""

class VariableUnbound(Exception):
    """Referenced variable is not bound to a value"""

class VariableAlreadyBound(Exception):
    """Referenced variable has been alreadly bound to a value"""

class NotUniqueCondition(Exception):
    """The belief set matching the condition is not unique"""

class InvalidTypeInCondition(Exception):
    """An argument in the condition expression is not of the valid type (i.e. Belief or lambda)"""

class NoMatchingPlanFound(Exception):
    """The Engine was unable to find a relevant plan, 
       i.e. a matching between the event and a triggering event"""

class InvalidTriggeringEvent(Exception):
    """ """

