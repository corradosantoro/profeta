#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
inference.py
"""

import copy
import time
import types
import random
import logging
import Queue
import threading

from profeta.exception import *
#import logger

from profeta.variable import *
from profeta.action import *
from profeta.profeta_globals import *
from profeta.attitude import *
from profeta.event import *

class KnowledgeBase(object):

    def __init__ (self, uEngine):
        self.__engine = uEngine
        self.__kb = []

    def __repr__ (self):
        return repr(self.__kb)

    def add_belief (self, uBelief):
        if not (uBelief.is_ground ()):
            raise NotGroundBelief (repr (uBelief))
        if uBelief.singleton():
            self.delete_belief_by_name(uBelief)
            uBelief.set_type(None)
            self.__kb.append (uBelief)
            return True
        else:
            if not (self.exists (uBelief)):
                #set belief type to None
                uBelief.set_type(None)
                self.__kb.append (uBelief)
                return True
            else:
                return False

    def delete_belief_by_name(self, uBelief):
        for b in self.__kb:
            if b.match_name(uBelief):
                #print "Current:", b
                self.delete_belief(b)
                #print "Next :", uBelief
                #                self.add_belief(uBelief)

    def delete_belief (self, uBelief):
        if not (uBelief.is_ground ()):
            raise NotGroundBelief (repr (uBelief))
        for b in self.__kb:
            if b.match(uBelief):
                self.__kb.remove (b)
                return True
        #print "No matching beliefs found for :",
        #print uBelief
        return False

    def exists (self, uBelief):
        for b in self.__kb:
          if b == uBelief:
            return True
        return False

    def beliefs_like_by_name(self, uBel):
        choices = []
        for b in self.__kb:
            if b.match_name (uBel):
                choices.append ( (b) )
        return choices


    def beliefs_like (self, uBel, uContext = {}):
        #print "$$$ Finding beliefs like ", uBel
        choices = []
        for b in self.__kb:
            #print "$$$ Selected", b
            Engine.instance().push_context(True)
            Engine.instance().set_context(copy.deepcopy(uContext))
            if b.unify(uBel):
                choices.append ( (b, Engine.instance().context()) )
            Engine.instance().pop_context()
        #print "$$$", choices
        return choices

    def one_belief (self):
        return random.choice (self.__kb)

    def one_belief_like (self, uBel):
        choices = []
        for b in self.__kb:
            if b.match (uBel):
                choices.append (b)
        if choices == []:
            return None
        else:
            ret_val = random.choice (choices)
            ret_val.unify(uBel)
            return uBel

    def one_belief_like_having_max (self, uBel, uFun):
        choices = []
        for b in self.__kb:
            Engine.instance().push_context(False)
            if b.unify (uBel):
                choices.append ((uFun(b), b, Engine.instance().context()))
            Engine.instance().pop_context()
        if choices == []:
            return None
        else:
            new_choices = []
            (max_val, selected_bel, selected_ctx) = choices [0]
            for (v, b, ctx) in choices [1:]:
                if v > max_val:
                    max_val = v
                    selected_bel = b
                    selected_ctx = ctx
            Engine.instance().set_context (selected_ctx)
            return selected_bel

    def one_belief_like_having_min (self, uBel, uFun):
        choices = []
        for b in self.__kb:
            Engine.instance().push_context(False)
            if b.unify (uBel):
                choices.append ((uFun(b), b, Engine.instance().context()))
            Engine.instance().pop_context()
        if choices == []:
            return None
        else:
            new_choices = []
            (min_val, selected_bel, selected_ctx) = choices [0]
            #print min_val, selected_bel
            for (v, b, ctx) in choices [1:]:
                #print v, b
                if v < min_val:
                    min_val = v
                    selected_bel = b
                    selected_ctx = ctx
            Engine.instance().set_context (selected_ctx)
            return selected_bel


class VersatileQueueFake(Queue.Queue):

    NORMAL_PUT = 0
    TOP_PUT = 1

    def _put (self, item):
        (data, mode) = item
        if mode == VersatileQueue.TOP_PUT:
            self.queue.appendleft(data)
        else:
            self.queue.append(data)

    # put the event at queue tail
    def put_event(self, uEvent):
        self._put ( (uEvent, VersatileQueue.NORMAL_PUT) )

    # put the event at queue head (so, this will be the first event to be dequeued)
    def put_top_event(self, uEvent):
        self._put ( (uEvent, VersatileQueue.TOP_PUT) )



class VersatileQueue:

    def __init__(self):
        self.__c = threading.Condition()
        self.__data = []
        self.__size = 0

    # put the event at queue tail
    def put_event(self, uEvent):
        self.__c.acquire()
        self.__data.append(uEvent)
        self.__size += 1
        self.__c.notify()
        self.__c.release()

    # put the event at queue head (so, this will be the first event to be dequeued)
    def put_top_event(self, uEvent):
        self.__c.acquire()
        self.__data.insert(0, uEvent)
        self.__size += 1
        self.__c.notify()
        self.__c.release()

    def get(self):
        self.__c.acquire()
        while self.__size == 0:
            self.__c.wait()
        item = self.__data.pop(0)
        self.__size -= 1
        self.__c.release()
        return item

    def wait_item(self):
        self.__c.acquire()
        while self.__size == 0:
            self.__c.wait()
        self.__c.release()

    def empty(self):
        self.__c.acquire()
        retval = self.__size == 0
        self.__c.release()
        return retval

    def has_a_top_goal(self):
        self.__c.acquire()
        if self.__size == 0:
            retval = False
        else:
            item = self.__data[0]
            s = item.__class__.__name__
            retval = s == "AddedGoalEvent" or s == "DeletedGoalEvent"
        self.__c.release()
        return retval


class Intention:

    def __init__(self, uEngine, uOriginatingEvent, uContext, uBody, uPriority = 0):
        self.__engine = uEngine
        self.__event = uOriginatingEvent
        self.__context = uContext
        self.__body = uBody
        self.__priority = uPriority

    def __repr__(self):
        return "%s >> %s" % (repr(self.__event), repr(self.__body))


    def get_originating_event(self):
        return self.__event


    def step(self):
        #print self.__body
        if self.__body == []:
            return False
        else:
            action_to_perform = self.__body[0]
            self.__body = self.__body[1:]

            self.__engine.set_context(self.__context)
            eval_globals = self.__engine.prepare_local_eval_context()
            #print action_to_perform.__class__
            #print eval_globals
            #print "---------------------"
            if isinstance(action_to_perform, Action):
                if PROFETA_LOGGING_ON:
                    self.__engine.get_logger().debug("Executing: " + repr(action_to_perform))
                eval_globals['__act'] = action_to_perform
                eval ("__act.run()", eval_globals)
            # if the selected action is the addition/deletion of a belief/goal:
            elif type(action_to_perform) == types.StringType:
                exec action_to_perform in eval_globals
            else:
                self.__engine.generate_internal_event(action_to_perform, None) #intention)
                #print action_to_perform#, eval_globals
            self.__engine.copy_to_context_from_globals(eval_globals)
            self.__context = self.__engine.context()
            return True


    def execute_all(self):
        while self.step():
            pass


class Engine(object):

    __instance = None
    __kb = None

    def __new__(cls):
        if Engine.__instance is None:
            Engine.__instance = object.__new__(cls)
            Variable.Engine = Engine.__instance
        return Engine.__instance


    def __init__ (self):
        self.__scheduler_tick = 0.01 # 10ms
        self.__event_pollers = []
        self.__knowledge_base = KnowledgeBase(self)
        Engine.__kb = self.__knowledge_base
        self.__context = {}
        self.__context_stack = []

        self.__plans = []
        self.__plan_cache = {}

        self.__plan_episode_cache = {}

        self.__current_episode = None
        self.__current_declared_episode = None

        self.__intentions = []
        self.__channel = VersatileQueue()

        self.__executor = None
        self.debug = False
        if PROFETA_LOGGING_ON:
            self.__logger = logging.getLogger("engine.Engine")
        else:
            self.__logger = None
    # obtaining __builtins__
        self.__eval_globals = {}
        eval ("True", self.__eval_globals)

    @classmethod
    def instance(cls):
        return cls.__instance

    @classmethod
    def kb(cls):
        return cls.__kb

    def get_logger(self):
        return self.__logger

    def get_scheduler_tick(self):
        return self.__scheduler_tick

    def set_scheduler_tick(self, uTickMS):
        self.__scheduler_tick = uTickMS / 1000.0

    def set_declared_episode (self, uEpisodeName):
        self.__current_declared_episode = uEpisodeName

    def set_current_episode (self, uEpisodeName):
        self.__current_episode = uEpisodeName

    def add_event_poller (self, uEventPoller):
        uEventPoller.prepare()
        self.__event_pollers.append (uEventPoller)

    def get_pollers (self):
        return self.__event_pollers

    def print_intentions(self):
        """Print all the intentions"""
        #for i in range(0,len(self.__intentions))
        print "INTENTIONS (outer): ",
        for (body,intention) in self.__intentions:
            print (body,intention)

    def print_plans(self, uPlans, uPlansKind):
        """ Bind each Variable contained into uPlans and then prints them """
        print ""
        print " ********************************* "
        print uPlansKind
        print " ********************************* "
        for (trigger, condition, body, context) in uPlans:
            self.set_context(context)
            print trigger, "|" , condition
            print "    >> "
            print "     ["
            if type(body) != types.ListType:
                print "     ", body
            else:
                for item in body:
                    print "       ", item
            print "     ]"
            self.clear_context()
            print ""


    def plans(self):
        return self.__plans


    def plan(self, uIndex):
        return self.__plans[uIndex]


    def plans_from_cache (self, uAttitude):
        classname = uAttitude.__class__.__name__  + "." + uAttitude.get_type() + "."
        if self.__plan_cache.has_key(classname):
            plans = map(lambda x: self.__plans[x], self.__plan_cache [classname])
        else:
            plans = []

        if self.__current_episode is not None:
            key = self.__current_episode + classname
            if self.__plan_cache.has_key(key):
                plans = plans + map(lambda x: self.__plans[x], self.__plan_cache [key])

        if plans == []:
            return None
        else:
            return plans


    def relevant_plans(self):
        return self.__relevant_plans

    def knowledge_base(self):
        return self.__knowledge_base

    def add_belief(self, uBelief):
        if uBelief.only_reactive():
            return True
        else:
            return self.__knowledge_base.add_belief(uBelief)

    def delete_belief_by_name(self, uBelief):
        if uBelief.only_reactive():
            return True
        else:
            return self.__knowledge_base.delete_belief_by_name(uBelief)

    def delete_belief(self, uBelief):
        if uBelief.only_reactive():
            return True
        else:
            return self.__knowledge_base.delete_belief( uBelief)

    def set_debug (self, uValue = True):
        self.debug = uValue

    def set_executor (self, uExecutor):
        self.__executor = uExecutor

    def put_event (self, uEvent):
        self.__channel.put_event( uEvent)

    def put_top_event (self, uEvent):
        self.__channel.put_top_event( uEvent)

    def add_plan (self, uPriority, uAttitude, uCondition, uBody):
        self.__plans.append( (uPriority, uAttitude, uCondition, uBody) )
        plan_index = len(self.__plans) - 1
        classname = uAttitude.__class__.__name__ + "." + uAttitude.get_type() + "."
        if self.__current_declared_episode is None:
            key = classname
        else:
            key = self.__current_declared_episode + classname

        if self.__plan_cache.has_key (key):
            cache = self.__plan_cache[key]
            cache.append (plan_index)
        else:
            self.__plan_cache[key] = [ plan_index ]


    def fail_current_goal(self):
        # determine current goal
        stack = []
        while self.__intentions != []:
            top = self.__intentions[0]
            evt = top.get_originating_event()
            #print evt
            if evt.is_goal():
                # the originating event is a goal, thus you can generate the goal failure event
                self.__intentions = self.__intentions[1:] # remove failed intention
                if not(evt.is_a_delete()):
                    fail_event = - evt
                    plan = self.plans_from_cache(fail_event)
                    # print fail_event, plan
                    if plan is not None:
                        # a plan is found
                        self.generate_internal_event(fail_event, None)
                        return
                    else:
                        stack.append(fail_event)
            else:
                # the originating event is NOT a goal, thus remove current intention
                self.__intentions = self.__intentions[1:] # remove failed intention
                print "Intention stopped due to a goal fail event: ", top
                break

        print "No goal failure catching plan for events: ", stack


    def pop_intention(self):
        return self.__intentions.pop()


    def push_intention(self, uInt):
        self.__intentions.append(uInt)


    def push_intention_as_first(self, uInt):
        self.__intentions.insert(0, uInt)


    def prepare_local_eval_context (self):
        eval_globals = self.__eval_globals.copy()
        for (key, value) in self.context().items():
            eval_globals['__builtins__'][key] = value
        return eval_globals


    def copy_to_context_from_globals(self, eval_globals):
        for (key, val) in eval_globals.items():
            if key != '__builtins__':
                #print "CTX", key, val
                self.__context[key] = val


    def execute(self):
        if self.__intentions != []:
            # if there are intentions to execute, execute one of it
            self.execute_one_intention()
            # if, after step execution, a goal is found on the top of the event queue
            # do not return and let the system to process it
            if not(self.__channel.has_a_top_goal()):
                return

        if self.__channel.empty():
            #time.sleep(self.__scheduler_tick)
            pollers = self.get_pollers()
            if pollers == []:
                self.__channel.wait_item()
            else:
                for poller in self.get_pollers():
                    event = poller.poll()
                    if event is not None:
                        if event.is_event() or event.get_type() is not None:
                            self.generate_external_event(event)
                        else:
                            self.add_belief(event)

        if not(self.__channel.empty()):
            event = self.__channel.get()
            if event is None:
                return
            relevant_plans =  self.evaluate_plans_from_event(event)
            applicable_plans = self.evaluate_conditions(relevant_plans)
            self.select_plan(applicable_plans)



    def evaluate_plans_from_event(self, uEvent):
        if PROFETA_LOGGING_ON:
            self.__logger.debug("Processing  " + repr(uEvent) )
        if self.debug:
            print "EVENT: " + repr(uEvent)

        candidate_plans = self.plans_from_cache (uEvent.get_attitude())
        if candidate_plans is None:
            return []  # no plans

        relevant_plans = []
        for (priority, trigger,condition,body) in candidate_plans:
            # make a copy of the trigger
            c_trigger = copy.deepcopy(trigger)
            # make a shallow copy of the the body
            # of the plan fetched from the plan library
            c_body = copy.copy(body)
            self.clear_context()
            if uEvent.unify(c_trigger):
                context = copy.deepcopy(self.context())
                #self.__logger.debug(repr(uEvent.get_attitude()) + "  unifies with  " + \
                #                     repr(c_trigger))
                #self.__logger.debug("Body of the plan that unifies: (%s)", body)
                relevant_plans.append( (priority, uEvent.get_attitude(), condition, c_body, context) )
            else:
                del c_trigger
                del c_body

        self.clear_context()
        if PROFETA_LOGGING_ON:
            self.__logger.debug("Found  " + repr(len(relevant_plans)) + "  RELEVANT plans for  " + repr(uEvent))
        #print relevant_plans
        if self.debug:
            print "FOUND: " + repr(len(relevant_plans)) + "  RELEVANT plans for  " + repr(uEvent)
            #for p in relevant_plans:
            #    print p
        return  relevant_plans


    def evaluate_conditions(self, uRelevantPlans):
        if PROFETA_LOGGING_ON:
            self.__logger.debug("Evaluating Condition for all Relevant Plans...")
        applicable_plans = []

        for relevant_plan in uRelevantPlans:
            (priority, trigger, condition, body, context) = relevant_plan
            self.__context = copy.deepcopy(context)

            if condition.evaluate():
                applicable_plans.append((priority, trigger, condition, body, copy.deepcopy(self.__context)))
                if self.debug:
                    print "CONDITION TRUE for PLAN: ", relevant_plan

        if PROFETA_LOGGING_ON:
            self.__logger.debug("Found  " + repr(len(applicable_plans)) + "  APPLICABLE plans")

        del uRelevantPlans ## would be cause of bugs?
        return applicable_plans



    def select_plan(self, uApplicablePlans):
        if PROFETA_LOGGING_ON:
            self.__logger.debug("Allocating Plans...")

        if uApplicablePlans != []:

            if self.debug:
                print "SELECTED: Plan " + repr(uApplicablePlans[0])

            # select first plan
            (priority, trigger, condition, body, context) = uApplicablePlans[0]

            if trigger.is_goal():
                #print "GOAL: ", trigger
                self.push_intention_as_first( Intention(self, trigger, context, body, priority) )
            else:
                #print "OTHER: ", trigger
                self.push_intention( Intention(self, trigger, context, body, priority) )


    def execute_one_intention(self):
        """ Selects an intention from self.__intentions and executes it."""

        #print self.__intentions

        # get first intention of the list
        intention = self.__intentions[0]
        if not(intention.step()):
            # if no more actions in the intention, remove it from queue
            self.__intentions = self.__intentions[1:]

    def intentions (self):
        return self.__intentions

    def num_intentions(self):
        return len(self.__intentions)

    def clear_context(self):
        self.__context = {}

    def context(self):
        return self.__context

    def set_context(self, uCtx):
        self.__context = uCtx

    def push_context(self, uClear):
        self.__context_stack.append (self.__context)
        if uClear:
            self.clear_context()

    def pop_context(self):
        self.clear_context()
        self.__context = self.__context_stack.pop ()

    def context_union(self, uCTXa, uCTXb):
        result_context = {}
        keys = {}
        for k in uCTXa.keys():
            keys[k] = True
        for k in uCTXb.keys():
            keys[k] = True
        for k in keys.keys():
            if uCTXa.has_key (k):
                result_context [k] = uCTXa[k]
            elif uCTXb.has_key (k):
                result_context [k] = uCTXb[k]
        return result_context

    def has_context_var(self, uVarName):
        return self.__context.has_key (uVarName)

    def get_context_var(self, uVarName):
        #print uVarName, self.__context[uVarName]
        return self.__context[uVarName]

    def set_context_var(self, uVarName, uVarValue):
        if uVarName == "_":
            return
        if self.has_context_var(uVarName):
            raise VariableAlreadyBound (uVarName)
        else:
            self.__context[uVarName] = uVarValue

    def generate_external_event(self, uBelief):
        """Invoked by sensors to pass their data to Engine

        It is assumed that an external event is pre-processed
        and represented as a Belief

        """
        if type(uBelief) == types.ListType:
            for belief in uBelief:
                evt = belief.create_event()
                evt.execute()
        else:
            evt = uBelief.create_event()
            evt.execute()

    def generate_final_event(self, uAttitude):
        if type(uAttitude) == types.ListType:
            for attitude in uAttitude:
                evt = attitude.create_event()
                evt.execute()
        else:
            evt = uAttitude.create_event()
            evt.execute()

    def generate_internal_event(self, Attitude, uIntention):
        # pass values to the new event
        uAttitude = copy.copy(Attitude)
        list_of_terms = uAttitude.get_terms()
        list_of_values = []
        for v in list_of_terms:
            if (isinstance(v, Variable)):
                list_of_values.append(v.get())
            else:
                list_of_values.append(v)

        uAttitude.set_terms(list_of_values)

        # Currently 'Test goal' are not supported, thus
        # when adding/removing Belief this method does nothing.
        # In fact, belief CAN NOT add information to context
        uAttitude.set_origin(uIntention)
        evt = uAttitude.create_event()
        evt.execute()

    def clear_all(self):
        self.__context = {}
        self.__context_stack = []
        self.__plans = []
        self.__plan_cache = {}
        self.__intentions = []
        self.__knowledge_base = KnowledgeBase(self)
        Engine.__kb = self.__knowledge_base


def CreateEngine(uTickMS = 10):
    e = Engine()
    e.set_scheduler_tick (uTickMS)
    return e


