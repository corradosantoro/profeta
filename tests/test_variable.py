# -*- coding: utf-8 -*-
import unittest

from profeta.inference import CreateEngine
from profeta.variable import Variable, make_terms

class VariableTestCase(unittest.TestCase):

    def setUp(self):
        CreateEngine()
        self.a_detective = Variable('Sherlock Holmes')

    def test_name(self):
        """Test the name of a variable."""
        self.assertEqual(self.a_detective.get_name(), 'Sherlock Holmes')

    def test_is_bound(self):
        """Test if a variable is bound."""
        self.assertEqual(self.a_detective.is_bound(), False)
        # Set a value make the variable bound
        self.test_set_get()
        self.assertEqual(self.a_detective.is_bound(), True)

    def test_is_unbound(self):
        """Test if a variable is unbound."""
        self.assertEqual(self.a_detective.is_unbound(), True)
        # Set a value make the variable bound
        self.test_set_get()
        self.assertEqual(self.a_detective.is_unbound(), False)

    def test_set_get(self):
        """Test set and get methods."""
        self.assertRaises(KeyError, self.a_detective.get)

        self.a_detective.set('Conan Doyle')
        self.assertEqual(self.a_detective.get(), 'Conan Doyle')
        self.assertNotEqual(self.a_detective.get(), 'Agatha Cristie')

    def test_match(self):
        """Test match method."""
        self.assertEqual(self.a_detective.match(Variable('_')), True)
        # Set a value for self.a_detective
        self.test_set_get()
        another_detective = Variable('Hercule Poirot')
        another_detective.set('Agatha Cristie')
        self.assertEqual(self.a_detective.match(another_detective), False)

    def test_match_value(self):
        """Test match_value method."""
        self.assertEqual(Variable('_').match_value('Anything!'), True)
        # Set a value for self.a_detective
        self.test_set_get()
        self.assertEqual(self.a_detective.match_value('Agatha Cristie'),
                             False)
        self.assertEqual(self.a_detective.match_value('Conan Doyle'), True)

    def test_getitem(self):
        """Test __getitem__ method."""
        # A not bound variable returns itself
        self.assertEqual(self.a_detective[0], self.a_detective)
        self.test_set_get()
        # A bound variable returns the index of the value. In this case value
        # is 'Conan Doyle'
        self.assertEqual(self.a_detective[0], 'C')

class MakeTermsTestCase(unittest.TestCase):

    def setUp(self):
        CreateEngine()

    def test_make_terms(self):
        """Test make_terms function."""
        terms = ['a', 'b']
        self.assertEqual(make_terms(terms), terms)
        terms = ['A', 'b']
        res = make_terms(terms)
        self.assertTrue(isinstance(res[0], Variable))
        self.assertEqual(res[0].get_name(), 'A')
        self.assertTrue(isinstance(res[1], basestring))
