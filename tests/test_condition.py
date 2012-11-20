# -*- coding: utf-8 -*-
import unittest

from profeta.inference import CreateEngine
from profeta.condition import Condition

class ConditionTestCase(unittest.TestCase):

    def setUp(self):
        CreateEngine()
        self.condition = Condition('A')

    def test_condition_instantiation(self):
        """Test Condition instantiation."""
        c = Condition()
        self.assertEqual(c._Condition__conditions, [])
        c = Condition('A')
        self.assertEqual(c._Condition__conditions, ['A'])
        c = Condition('A', 'B')
        self.assertEqual(c._Condition__conditions, ['A', 'B'])

    def test_append(self):
        """Test Condition append method."""
        self.condition.append('B')
        self.assertEqual(self.condition._Condition__conditions, ['A', 'B'])

    def test_insert_at_top(self):
        """Test Condition instert_at_top method."""
        self.condition.insert_at_top('B')
        self.assertEqual(self.condition._Condition__conditions, ['B', 'A'])

    def test_and(self):
        """Test and bitwise overload"""
        result = self.condition & 'B'
        self.assertEqual(self.condition._Condition__conditions, ['A', 'B'])
