#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
attitude.py
"""

from event import *
from condition import *
from inference import *
#Engine
#from inference import Variable

__all__ = ['Attitude', 'Belief', 'SingletonBelief', 'Reactor', 'Goal' ]

class Attitude(object):

    def __init__(self, *args, **kwargs):
        self.__condition = TrueCondition()
        # 0 means lowest priority
        self._priority = 0
        self._type = None
        self._originating_intention = None
        # _terms contains all the arguments
        # of the Attitude
        self._terms = make_terms(args)
        #self._terms = []
        #for i in range (0, len(args)):
        #    self._terms.append (args [i])

    def is_event(self):
        return False

    def is_goal(self):
        return False

    def only_reactive(self):
        return False

    def singleton(self):
        return False

    def get_terms(self):
        return self._terms

    def set_terms(self, *args, **kwargs):
        self._terms = []
        for i in range(0, len(args[0])):
            self._terms.append(args[0][i])

    def __pos__(self):
        self._type = "add"
        return self

    def __neg__(self):
        self._type = "delete"
        return self

    def __div__(self, uTerm):
        """
        Overriding of operator `/` used as a separator between Triggering
        Event and Condition.
        """
        # The condition is made of a single term which is a function.
        # Note: no more than one function is allowed in the condition.
        if uTerm.__class__.__name__ == 'function':
            c = Condition(uTerm)
            self.set_condition(c)
            return self
        # The condition is made of a single term which is a Belief
        elif isinstance(uTerm, Belief):
            c = Condition(uTerm)
            self.set_condition(c)
            return self
        # The condition is a Condition object, i.e. it is a list of terms
        elif isinstance(uTerm, Condition):
            self.set_condition(uTerm)
            return self
        else:
            raise InvalidTypeInCondition(repr(uTerm))

    def __rmod__(self, uTerm):
        """Ovverriding of operator `%` (right side) to define a priority for
        the plan.
        """
        self._priority = uTerm
        #print "The priority is: ", self._priority
        return self

    def __rshift__(self, uRHS):
        """Overriding of operator `>>` used as a separator between Head and
        Body of the plan.
        The plan is added in the Engine.
        """
        if self._type is not None:
            Engine.instance().add_plan(self._priority,
                                       self,
                                       self.__condition,
                                       uRHS)
            return self
        else:
            raise InvalidTriggeringEvent()

    def set_condition(self, uCondition):
        self.__condition = uCondition

    def get_condition(self):
        return self.__condition

    def set_priority(self, uPriority):
        self._priority = uPriority

    def get_priority(self):
        return self._priority

    def set_origin(self, uIntention):
        #self._originating_intention = uIntention
        pass

    def get_origin_body(self):
        return self._originating_intention[0]

    def get_origin(self):
        return self._originating_intention

    def set_type(self, uType):
        self._type = uType

    def get_type(self):
        return self._type

    def is_a_delete(self):
        return self._type == "delete"

    def unify(self, uAnotherAttitude):
        """Template method used to unify two attitudes"""
        if not self.do_check_class_names(uAnotherAttitude):
            return False
        if not self.do_check_event_type(uAnotherAttitude):
            return False
        if not self.do_check_number_of_terms(uAnotherAttitude):
            return False
        return (self.do_compare_attitude_values_with_trigger_terms(uAnotherAttitude) or
                self.do_compare_attitude_terms_with_trigger_terms(uAnotherAttitude))

    def do_check_class_names(self, uAnotherAttitude):
        """Compares the classobj of two attitudes."""
        if self.__class__ != uAnotherAttitude.__class__:
            #print self.__class__,
            #print "   VS.   ",
            #print uAnotherAttitude.__class__
            return False
        return True

    def do_check_event_type(self, uAnotherAttitude):
        """ Check if both events are of the same type"""
#         print self._type
#         print uAnotherAttitude._type
        if self._type == uAnotherAttitude._type:
            return True
        return False

    def do_check_number_of_terms(self, uAnotherAttitude):
        """Check if the list of terms of two attitudes have the same size."""
        self_terms = self._terms
        other_terms = uAnotherAttitude.get_terms()
        if len(self_terms) != len(other_terms):
            return False
        return True

    def do_compare_attitude_values_with_trigger_terms(self, uAnotherAttitude):
        """ Compare the values of the arguments of self attitude
        with the terms of another Attitude

        This methods works if the arguments of self attitude are
        value terms
        Ex. move(100)

        If one of the arguments is not a value term, this method
        return False
        """
        self_terms = self._terms
        other_terms = uAnotherAttitude.get_terms ()
        # Compare every term of the attitude  with the term
        # of the current trigger
        #print "COMPARING", self_terms, other_terms
        for i in range(0, len(self_terms)):
            a = self_terms[i]
            b = other_terms[i]
            # The attitude has a value term and the triggering event
            # has a variable term.
            # Ex. move(100)  vs  move(X)
            if (not isinstance(a, Variable)) and (isinstance (b, Variable)):
                # If b is not present in the context, assign it.
                # In the previous example, X=100
                if b.is_unbound():
                    b.set (a)
                # If b is already present in the context, his value must
                # match a.
                # Ex.  goal(100,3,70) is not unified with goal(X,Y,X)
                else:
                    if not (b.match_value (a)):
                        return False
            # The attitude and the trigger have both value terms.
            # Ex. move(100)  vs move(200).
            # A simple test of the equality of the two values is performed
            elif (not isinstance(a, Variable)) and (not isinstance (b, Variable)):
#                print "I'm in ELIF", a.__class__ , b.__class__
                if a != b:
#                    print "I'm in ELIF 2!", a, b
                    return False
            else:
                return False
        return True

    def do_compare_attitude_terms_with_trigger_terms(self, uAnotherAttitude):
        """Compare the arguments of self attitude with the terms of another
        Attitude.

        This methods works if the arguments of self attitude
        are Variable terms
        Ex. move(X)

        If one of the arguments is not a Variable term,
        this method return False
        """
        return False


class Belief(Attitude):

    def __init__(self, *args, **kwargs):
        Attitude.__init__(self,*args, **kwargs)
        self._type = None

    def __repr__(self):
        if len(self._terms) is not 0:
            repr_string =  self.__class__.__name__ + "(" + \
                    reduce (lambda x,y : x + "," + y,
                            map (lambda x: repr(x), self._terms)) + \
                    ")"
        else:
            repr_string =  self.__class__.__name__ + "()"
        return repr_string

    #def set_origin(self, uIntention):
    #    self._originating_intention = None


    def match_name(self, uAnotherBel):
        if self.__class__ != uAnotherBel.__class__:
            return False
        if self.__class__.__name__ != uAnotherBel.__class__.__name__:
            return False
        #print self.__class__.__name__
        return True

    def __and__(self, uOther):
        if isinstance (uOther, Belief):
            return Condition (self, uOther)
        elif isinstance (uOther, Condition):
            uOther.insert_at_top (self)
            return uOther
        elif type(uOther) == types.FunctionType:
            return Condition (self, uOther)
        else:
           raise InvalidTypeInCondition (repr (uOther))

    def __getitem__(self, uItem):
        return self.v(uItem)

    def __setitem__(self, uItem, uValue):
        return self.sv(uItem, uValue)

    def v(self, uIndex):
        t = self._terms[uIndex]
        if isinstance (t, Variable):
            return t.get()
        else:
            return t

    def sv(self, uIndex, uValue):
        t = self._terms[uIndex]
        if isinstance (t, Variable):
            t.set(uValue)
        else:
            self._terms[uIndex] = uValue

    def create_event(self):
        if self._type == "add":
            return AddedBeliefEvent(self)
        elif self._type == "delete":
            return DeletedBeliefEvent(self)
        else:
            raise BeliefEventTypeNotDefined()

    def is_ground(self):
        for term in self._terms:
            if isinstance (term, Variable):
                if term.is_unbound():
                    return False
        return True

    # This requires that self and uOther are ground terms
    def __eq__(self, uOther):
        if not (self.is_ground()) or not (uOther.is_ground()):
            raise NotGroundBelief(repr(self) + " or " + repr(uOther))
        if self.__class__ != uOther.__class__:
            return False
        self_terms = self._terms
        other_terms = uOther.get_terms ()
        if len (self_terms) != len (other_terms):
            return False
        for i in range (0, len(self_terms)):
            a = self_terms[i]
            b = other_terms[i]
            if a != b:
                #print "Comparing ", self, " and ", uOther, ": different"
                return False
        #print "Comparing ", self, " and ", uOther, ": SAME"
        return True

    # This method is used when we want to select some beliefs
    # i.e. one_belief_like
    def match(self, uAnotherBel):
        if self.__class__ != uAnotherBel.__class__:
            return False
        self_terms = self._terms
        other_terms = uAnotherBel.get_terms ()
        if len (self_terms) != len (other_terms):
            return False
        for i in range (0, len(self_terms)):
            a = self_terms[i]
            b = other_terms[i]

            if (isinstance(a, Variable)) and (isinstance(b, Variable)):
                if b.is_unbound():
                    raise VariableUnbound (repr(a))

                if (a.is_bound()) and not (a.match(b)):
                    return False
            elif (not isinstance(a, Variable)) and (isinstance (b, Variable)):
                if (b.is_bound()) and not (b.match_value (a)):
                    return False
            elif (isinstance(a, Variable)) and (not isinstance (b, Variable)):
                if (a.is_bound()) and not (a.match_value (b)):
                    return False
            else:
                if a != b:
                    return False
        return True


    def do_compare_attitude_terms_with_trigger_terms(self, uAnotherAttitude):
        # Compare every term of the attitude  with the term
        # of the current trigger
        self_terms = self._terms
        other_terms = uAnotherAttitude.get_terms ()
        for i in range (0, len(self_terms)):
            a = self_terms[i]
            b = other_terms[i]
            # The attitude and the trigger have both variable terms.
            # Ex. move(X,Y) vs move(K,Z)
            if (isinstance(a, Variable)) and (isinstance(b, Variable)):
                if b.is_unbound():
                    raise VariableUnbound (repr(a))
                if a.is_unbound():
                    a.set(b.get())
                else:
                    if not (a.match(b)):
                        return False
            # The attitude has a variable term and the trigger has a value
            # term. The opposite of the previous situation.
            # It is used when unifying an element of the condition with the
            # KnowledgeBase.
            # Ex. position(X,Y) vs position(100,200)
            elif (isinstance(a, Variable)) and (not isinstance (b, Variable)):
                if a.is_unbound():
                    a.set (b)
                else:
                    if not (a.match_value (b)):
                        return False
            else:
                return False
        return True


class Goal(Attitude):

    def __init__(self, *args, **kwargs):
        Attitude.__init__(self,*args, **kwargs)
        self._type = "add"  # the default event is "+"

    def __repr__(self):
        if len(self._terms) is not 0:
            repr_string = self.__class__.__name__ + "(" + \
                    reduce (lambda x,y : x + "," + y,
                            map (lambda x: repr(x), self._terms)) + \
                    ")"
        else:
            repr_string =  self.__class__.__name__ + "()"
        if self._type == "add":
            return "+~" + repr_string
        else:
            return "-~" + repr_string

    def is_goal(self):
        return True

    def set_origin(self, uIntention):
        self._originating_intention = uIntention

    def __invert__ (self):
        return self

    def create_event(self):
        if self._type == "add":
            return AddedGoalEvent(self)
        elif self._type == "delete":
            return DeletedGoalEvent(self)
        else:
            raise GoalEventTypeNotDefined()


class SingletonBelief(Belief):

    def singleton(self):
        return True


class Reactor(Belief):

    def only_reactive(self):
        return True



