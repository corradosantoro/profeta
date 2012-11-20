#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
threaded_engine_executor.py
"""

import threading
import Queue
import logging
import time

from profeta_globals import *


class AbstractEngineExecutor(object):

    def __init__ (self, uEngine):
        self.engine = uEngine

    def start(self):
        raise "not implemented"

    def execute (self):
        raise "not implemented"


class VersatileQueue(Queue.Queue):

    NORMAL_PUT = 0
    TOP_PUT = 1

    def _put (self, item):
        (data, mode) = item
        if mode == VersatileQueue.TOP_PUT:
            self.queue.appendleft(data)
        else:
            self.queue.append(data)




#
# threaded_engine_executor.py
#

class ThreadedEngineExecutor(AbstractEngineExecutor,threading.Thread):

    def __init__ (self, uEngine):
        threading.Thread.__init__ (self)
        AbstractEngineExecutor.__init__ (self, uEngine)
        self.engine.set_executor (self)
        self.__channel = VersatileQueue ()
        self.setDaemon(True)
        if PROFETA_LOGGING_ON:
            self.__logger = logging.getLogger("engine.Thread")
        else:
            self.__logger = None

    def start (self):
        threading.Thread.start(self)

    def put_event (self, uEvent):
        self.__channel.put ( (uEvent, VersatileQueue.NORMAL_PUT) )

    def put_top_event (self, uEvent):
        self.__channel.put ( (uEvent, VersatileQueue.TOP_PUT) )

    def   run (self):
        if PROFETA_LOGGING_ON:
            self.__logger.info("Threaded Engine Executor started")

        event_pollers = self.engine.get_pollers()

        while True:

            if PROFETA_LOGGING_ON:
                self.__logger.debug("Waiting for an Event... (num_intention = %d)\n" % (self.engine.num_intentions()))

            # fetch an event
            if ( self.__channel.empty() and (self.engine.num_intentions() > 0)):
                #print "There are intentions: ",
                #print self.engine.intentions()
                self.engine.execute_intentions()
                continue
            else :
                #print "\nWaiting for an event ..."
                if event_pollers == []:
                    event = self.__channel.get ()
                else:
                    for poller in event_pollers:
                        poller.poll()
                    if self.__channel.empty():
                        time.sleep(self.engine.get_scheduler_tick())
                        continue
                    else:
                        event = self.__channel.get ()

                #print "Processing:  ", event

            # determine the relevant plans
            relevant_plans =  self.engine.process_event (event)
            # print event, relevant_plans
            #self.engine.print_plans(relevant_plans, " Relevant Plans: ")

            # if there are relevant plans, determine which of them are applicable
            if len(relevant_plans) is not 0:
                applicable_plans = self.engine.evaluate_condition(relevant_plans)
                # print "applicable", applicable_plans
            # else, execute the next intention
            else:
                self.engine.execute_intentions()
                continue

            # if there are applicable plans, allocate them
            if len(applicable_plans) is not 0:
                trigger = self.engine.allocate_plans(applicable_plans)
                self.engine.execute_intentions(trigger)
            #else, execute the next intention
            else:
                self.engine.execute_intentions()
                continue

