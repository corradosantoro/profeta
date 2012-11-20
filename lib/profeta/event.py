#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
event.py
"""

import copy
from inference import Engine


class Event(object):
    def __init__ (self, uAttitude):
        self._attitude = uAttitude

    def execute(self):
        pass

    def get_condition (self):
        return self._attitude.get_condition()

    def get_attitude(self):
        return self._attitude

    def unify(self, trigger):
        return self._attitude.unify (trigger)


class AddedBeliefEvent(Event):

    def __init__ (self, uBelief):
        Event.__init__ (self,uBelief)

    def execute (self):
        attitude = copy.deepcopy(self._attitude)
        if Engine.instance().add_belief (attitude):
            Engine.instance().put_event(self)

    def __repr__ (self):
        return "+" + repr (self._attitude)

    def __str__ (self):
        return self.__repr__()


class DeletedBeliefEvent(Event):

    def __init__ (self, uBelief):
        Event.__init__ (self,uBelief)

    def __repr__(self):
        return "-" + repr (self._attitude)

    def execute (self):
        attitude = copy.deepcopy(self._attitude)
        if Engine.instance().delete_belief (attitude):
            Engine.instance().put_event(self)


class AddedGoalEvent(Event):

    def __init__ (self, uGoal):
        Event.__init__ (self,uGoal)

    def __repr__(self):
        return repr (self._attitude)

    def execute (self):
        Engine.instance().put_top_event(self)


class DeletedGoalEvent(Event):

    def __init__ (self, uGoal):
        Event.__init__ (self,uGoal)

    def __repr__(self):
        return repr (self._attitude)

    def execute (self):
        Engine.instance().put_event(self)

