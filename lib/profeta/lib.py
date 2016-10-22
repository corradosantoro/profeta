#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
lib.py
"""

import threading

from profeta.attitude import *
from profeta.inference import *
from profeta.main import *

class start(Reactor):
    pass


global start_event
start_event = +start()


# ------------------------------------------------------------------------------
def declare_episode(uEpisodeName):
    Engine.instance().set_declared_episode(uEpisodeName)

def context(uGoalName):
    declare_episode(uGoalName)

def stage(uGoalName):
    declare_episode(uGoalName)

# ------------------------------------------------------------------------------
class start_episode(Action):

    def init(self):
        self.__e = Engine.instance()

    def execute(self):
        self.__e.set_current_episode(self[0])
        global start_event
        self.__e.generate_external_event (start_event)


# ------------------------------------------------------------------------------
class set_context(start_episode):
    pass


# ------------------------------------------------------------------------------
class set_stage(start_episode):
    pass


# ------------------------------------------------------------------------------
class nop(Action):

    def execute(self):
        pass


# ------------------------------------------------------------------------------
class fail(Action):

    def execute(self):
        Engine.instance().fail_current_goal()


# ------------------------------------------------------------------------------
class show(Action):

    FIND_BEGIN_MARK = 0
    FIND_END_MARK = 0

    def do_print(self, s):
        state = show.FIND_BEGIN_MARK
        for idx in range(0, len(s)):
            if state == show.FIND_BEGIN_MARK:
                if s[idx] == '?':
                    s_marker = idx
                    state = show.FIND_END_MARK
                else:
                    print s[idx],
            elif state == state.FIND_END_MARK:
                if s[idx] == '?':
                    print '?',
                    state = show.FIND_BEGIN_MARK
                if not(s[idx].isalnum()):
                    e_marker = idx
                    varname = s[s_marker:e_marker]

    def execute(self):
        for i in range(0, self.items()):
            print self[i],


# ------------------------------------------------------------------------------
class show_line(Action):

    def execute(self):
        for i in range(0, self.items()):
            print self[i],
        print

# ------------------------------------------------------------------------------
class OneShotPoller:

    def __init__ (self, uAutoRearm = False):
        self.__rearm = uAutoRearm
        self.__active = False
        self.__e = Engine.instance()
        self.init()

    def init(self):
        raise "NotImplemented"

    def activate(self):
        self.__active = True

    def suspend(self):
        self.__active = False

    def is_active(self):
        return self.__active

    def do_poll(self):
        if self.__active:
            bel = self.poll()
            if bel is not None:
                self.__e.generate_external_event(+bel)
                if not(self.__rearm):
                    self.__active = False

    def poll(self):
        raise "NotImplemented"



# ------------------------------------------------------------------------------
class RepetitivePoller(OneShotPoller):

    def __init__ (self):
        OneShotPoller.__init__ (self, True)


# ------------------------------------------------------------------------------
class Sensor:

    def __init__(self, do_start = True):
        self.__initial_on = do_start
        self.__is_on = None

    def on(self):
        if self.__is_on is not None:
            self.__is_on = True
            self.resume()
        else:
            self.__is_on = True

    def off(self):
        if self.__is_on is not None:
            self.__is_on = False
            self.suspend()

    def is_on(self):
        return self.__is_on

    def prepare(self):
        if self.__initial_on:
            self.on()
        self.start()

    def poll(self):
        if self.is_on():
            return self.sense()
        else:
            return None

    def start(self):
        pass

    def sense(self):
        raise "Not implemented"

    def suspend(self):
        pass

    def resume(self):
        pass


# ------------------------------------------------------------------------------
class sensor_on(Action):

    def execute(self):
        s = self[0]
        for p in Engine.instance().get_pollers():
            if isinstance(p, s):
                p.on()


# ------------------------------------------------------------------------------
class sensor_off(Action):

    def execute(self):
        s = self[0]
        for p in Engine.instance().get_pollers():
            if isinstance(p, s):
                p.off()


# ------------------------------------------------------------------------------
