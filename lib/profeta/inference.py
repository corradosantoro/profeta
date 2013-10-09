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

from profeta.exception import *
#import logger

from profeta.variable import *
from profeta.action import *
from profeta.profeta_globals import *
from profeta.attitude import *

class KnowledgeBase(object):

    def __init__ (self, uEngine):
        self.__engine = uEngine
        self.__kb = []

    def __repr__ (self):
        return repr(self.__kb)

    def add_belief (self, uBelief):
        if not (uBelief.is_ground ()):
            raise NotGroundBelief (repr (uBelief))
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
        choices = []
        for b in self.__kb:
            Engine.instance().push_context(True)
            Engine.instance().set_context(uContext)
            if b.unify (uBel):
                choices.append ( (b, Engine.instance().context()) )
            Engine.instance().pop_context()
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
        classname = uAttitude.__class__.__name__
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
        self.__executor.put_event( uEvent)

    def put_top_event (self, uEvent):
        self.__executor.put_top_event( uEvent)

    def add_plan (self, uPriority, uAttitude, uCondition, uBody):
        self.__plans.append( (uPriority, uAttitude, uCondition, uBody) )
        plan_index = len(self.__plans) - 1
        classname = uAttitude.__class__.__name__
        if self.__current_declared_episode is None:
            key = classname
        else:
            key = self.__current_declared_episode + classname

        if self.__plan_cache.has_key (key):
            cache = self.__plan_cache[key]
            cache.append (plan_index)
        else:
            self.__plan_cache[key] = [ plan_index ]


    def pop_intention(self):
        return self.__intentions.pop()

    def push_intention(self, uPlan):
        self.__intentions.append(uPlan)

    def prepare_local_eval_context (self):
        eval_globals = self.__eval_globals.copy()
        for (key, value) in self.context().items():
            eval_globals['__builtins__'][key] = value
        return eval_globals

    def process_event (self, uEvent):
        if PROFETA_LOGGING_ON:
            self.__logger.debug("Processing  " + repr(uEvent) )

        relevant_plans = []
        #for (priority, trigger,condition,body) in self.__plans:
        candidate_plans = self.plans_from_cache (uEvent.get_attitude())
        if candidate_plans is None:
            return relevant_plans
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
#         for (trigger, condition, body, context) in relevant_plans:
#             self.__logger.debug("(%s,%s)", body, context)
        return  relevant_plans


    def evaluate_condition(self, uRelevantPlans):
        if PROFETA_LOGGING_ON:
            self.__logger.debug("Evaluating Condition for all Relevant Plans...")
        applicable_plans = []

        for relevant_plan in uRelevantPlans:
            (priority, trigger, condition, body, context) = relevant_plan
            self.__context = copy.deepcopy(context)

            if condition.evaluate():
                applicable_plans.append((priority, trigger, condition, body, copy.deepcopy(self.__context)))

        if PROFETA_LOGGING_ON:
            self.__logger.debug("Found  " + repr(len(applicable_plans)) + "  APPLICABLE plans")

        del uRelevantPlans ## would be cause of bugs?
        return applicable_plans

    def allocate_plans(self, uApplicablePlans):
        if PROFETA_LOGGING_ON:
            self.__logger.debug("Allocating Plans...")
        for plan in uApplicablePlans:
            (priority, trigger, condition, body, context) = plan
            # if the trigger event is an external event, it has no origin associated
            # so, the plan has to be allocated as a new intention
            if trigger.get_origin() is None:
                if PROFETA_LOGGING_ON:
                    self.__logger.debug("External event: creating new Intention...")
                # Insert applicable plans in the Intentions stack ordered by
                # priority. 0 is the lowest priority
                #self.__intentions.insert(priority, [(priority, body, context)] )
                #self.__logger.debug("Intentions is: " + repr(self.__intentions))
                pr_index = 0
                intention_added = 0
                # Currently there are no intention
                if len(self.__intentions) is 0:
                    self.__intentions.append( [(priority, body, context)] )
                else:
                    # Insert intention according to priorities
                    for intention in self.__intentions:
                        # The empty intention may be used for pushing other
                        # plans
                        if len(intention) is not 0:
                            # Every Intention has the template:[(priority, body, context)]
                            intention_item = intention[0]
                            ( curr_pr, curr_body, curr_ctx) = intention_item
                            if priority > curr_pr:
                                pr_index+=1
                                continue
                            self.__intentions.insert(pr_index, [(priority, body, context)])
                            intention_added = 1
                            break
                    # The plan has the highest priority
                    if intention_added is 0:
                            self.__intentions.append([(priority, body, context)])
            # else, if the triggering event was an internal event, the associated plan
            # has to be allocated on the top of the originating intention
            else:
                if PROFETA_LOGGING_ON:
                    self.__logger.debug("Internal event: pushing body in " + repr(trigger.get_origin()))
                # The pushed plan inherit the priority of the containing plan
                trigger.get_origin().insert(0,(priority,body,context))
                if PROFETA_LOGGING_ON:
                    self.__logger.debug("Intentions is: " +
                                        repr(self.__intentions))
        return trigger

    def execute_intentions (self, trigger = None):
        """ Selects an intention from self.__intentions and executes it."""
        # Check for empty intentions and remove them
        for intention in self.__intentions:
            if len(intention) is 0:
                if PROFETA_LOGGING_ON:
                    self.__logger.debug("Removing empty intention: %s" , intention)
                self.__intentions.remove(intention)
                #print "REMOVED : ", self.__intentions
                if PROFETA_LOGGING_ON:
                    self.__logger.debug("New list of intentions: %s ", self.__intentions)

        #if there're no intentions to execute
        if len(self.__intentions) is 0:
            #print "There are no intentions : ",
            #print self.__intentions
            #is an exception suitable here?
            return

        # now the select the next intention to execute
        # if no applicable plans were found
        if trigger is None:
            intention = self.__intentions[-1]
        # else if a plan has been triggered by an external event
        elif trigger.get_origin() is None:
            intention = self.__intentions[-1]
        # else if a plan has been triggered by an external event
        else:
            intention = trigger.get_origin()

        top_of_intention = intention[0]
        (priority, body, context) = top_of_intention
        self.__context = context.copy()
        if self.debug:
            print "Executing ", body  , " with context ", context

        if len(body) is not 0:
            if PROFETA_LOGGING_ON:
                self.__logger.debug("Old list of intentions: %s ", self.__intentions)
            action_to_perform = body[0]
            body.remove(action_to_perform)

            # if the selected action is an object of class Action:
            if isinstance(action_to_perform, Action):
                if PROFETA_LOGGING_ON:
                    self.__logger.debug("Executing: " + repr(action_to_perform))
                eval_globals = self.prepare_local_eval_context()
                eval_globals['__act'] = action_to_perform
                eval ("__act.run()", eval_globals)
                # If an Action is the last element of the body, remove the
                # entire body
                for intention in self.__intentions:
                    if len(intention) is 0:
                        if PROFETA_LOGGING_ON:
                            self.__logger.debug("Removing empty intention: %s" , intention)
                        self.__intentions.remove(intention)
                        if PROFETA_LOGGING_ON:
                            self.__logger.debug("New list of intentions: %s ", self.__intentions)


            # if the selected action is the addition/deletion of a belief/goal:
            else:
                self.generate_internal_event(action_to_perform, intention)

            # if there're no more action to perform in this plan:
            if len(body) is 0:
                if PROFETA_LOGGING_ON:
                    self.__logger.debug("Plan completed! Removing it from the stack...")
                    self.__logger.debug("Removing: %s from intention %s" , top_of_intention, intention)
                intention.remove(top_of_intention)
                if PROFETA_LOGGING_ON:
                    self.__logger.debug("New list of intentions: %s ", self.__intentions)
        else:
            if PROFETA_LOGGING_ON:
                self.__logger.debug("Warning: empty plan into self.__intentions")

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
        list_of_values = list_of_terms
        if len(list_of_terms) is not 0:
            if (isinstance(list_of_terms[0], Variable)):
                list_of_values = map ( lambda x : x.get(),
                                       list_of_terms)

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


