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
class nop(Action):

    def execute(self):
        pass


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

    def __init__(self):
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
        self.start()

    def poll(self):
        if self.is_on():
            return self.sense()
        else:
            return None

    def start(self):
        self.on()

    def sense(self):
        raise "Not implemented"

    def suspend(self):
        pass

    def resume(self):
        pass

# ------------------------------------------------------------------------------
class SynchSensor(Sensor):

    def __init__(self):
        Sensor.__init__(self)

# ------------------------------------------------------------------------------
class ASynchSensor(Sensor, threading.Thread):

    def __init__(self, uPeriodMS = 100):
        self.__period = uPeriodMS / 1000.0
        self.__last_data = None
        self.__lock = threading.Lock()
        Sensor.__init__(self)
        threading.Thread.__init__(self)

    def prepare(self):
        Sensor.prepare(self)
        threading.Thread.start(self)
        self.setDaemon(True)

    def poll(self):
        if self.is_on():
            try:
                self.__lock.acquire()
                return self.__last_data
            finally:
                self.__last_data = None
                self.__lock.release()
        else:
            return None

    def run(self):
        while True:
            if self.is_on():
                data = self.sense()
                if data is not None:
                    self.__lock.acquire()
                    self.__last_data = data
                    self.__lock.release()
            time.sleep(self.__period)



