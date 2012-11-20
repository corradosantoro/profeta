# -*- coding: utf-8 -*-
import unittest

from profeta.attitude import Attitude, Belief, Goal
from profeta.condition import Condition, TrueCondition
from profeta.inference import CreateEngine, Engine
from profeta.exception import InvalidTypeInCondition, InvalidTriggeringEvent

class AttitudeTestCase(unittest.TestCase):

    def setUp(self):
        CreateEngine()
        self.attitude = Attitude()

    def test_priority(self):
        """Test set/get priority."""
        self.attitude.set_priority(1)
        self.assertEqual(self.attitude.get_priority(), 1)

    def test_terms(self):
        """Test set/get terms."""
        terms = ['ball', 42, 42]
        self.attitude.set_terms(terms)
        self.assertEqual(self.attitude.get_terms(), terms)

    def test_condition(self):
        """Test set/get condition"""
        condition = Condition('A')
        self.attitude.set_condition(condition)
        self.assertEqual(self.attitude.get_condition(), condition)

    def test_type(self):
        """Test set/get type."""
        self.attitude.set_type('add')
        self.assertEqual(self.attitude.get_type(), 'add')

    def test_pos(self):
        """Test __pos__ method."""
        self.aptitude = +self.attitude
        self.assertEqual(self.attitude.get_type(), 'add')

    def test_neg(self):
        """Test __neg__ method."""
        self.aptitude = -self.attitude
        self.assertEqual(self.attitude.get_type(), 'delete')

    def test_or(self):
        """Test __or__ method."""
        # function
        x = lambda: 42
        res = self.attitude | x
        self.assertEqual(res.get_condition()._Condition__conditions[0], x)

        # Belief
        class object_seen(Belief):
            pass
        res = self.attitude | object_seen('x')
        self.assertEqual(res.get_condition()._Condition__conditions[0],
                             object_seen('x'))
        # Condition
        condition = Condition('A')
        res = self.attitude | condition
        self.assertEqual(res.get_condition(), condition)
        # raise InvalidTypeInCondition
        self.assertRaises(InvalidTypeInCondition,
                              lambda: self.attitude | None)

    def test_rmod(self):
        """Test __rmod__ method."""
        res = 2 % self.attitude
        self.assertEqual(self.attitude.get_priority(), 2)

    def test_rshift(self):
        """Test __rshift__ method."""
        class reach_object(Goal):
            pass
        action = reach_object('1', '1')
        # If self.attitude type is None InvalidTriggeringEvent will raised
        self.assertRaises(InvalidTriggeringEvent,
                              lambda: self.attitude >> action)

        res = +self.attitude >> action
        self.assertEqual(res, self.attitude)
        self.assertEqual(Engine.instance().plans(),
                         [(0, self.attitude, TrueCondition(), action)])

class MultipleAttitudeTestCase(unittest.TestCase):

    def setUp(self):
        CreateEngine()

        class A(Attitude):
            pass
        class B(Attitude):
            pass

        self.a = A('1', '2')
        self.b = B('1', '2')
        self.c = A('1')

    def test_do_check_class_names(self):
        """Test attitude class names."""
        self.assertTrue(self.a.do_check_class_names(self.a))
        self.assertFalse(self.a.do_check_class_names(self.b))

    def test_do_check_event_type(self):
        """Test attitude event type."""
        self.assertEqual(self.a.get_type(), None)
        self.assertEqual(self.b.get_type(), None)
        self.assertTrue(self.a.do_check_event_type(self.a))

        self.a = +self.a
        self.assertFalse(self.a.do_check_event_type(self.b))

    def test_do_check_number_of_terms(self):
        """Test attitude number of terms."""
        self.assertTrue(self.a.do_check_number_of_terms(self.b))
        self.assertFalse(self.a.do_check_number_of_terms(self.c))
