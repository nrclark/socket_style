#!/usr/bin/env python

import sys, os
import unittest

script_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.join(script_dir, os.path.pardir)
sys.path.append(os.path.normpath(parent_dir))

class TestImports(unittest.TestCase):
    """Tests to ensure that the unit-test framework is working."""

    def test_basic(self):
        import SocketStyle
        self.assertTrue(True)

    def test_does_false_work(self):
        self.assertFalse(False)

class FunctionalTest(unittest.TestCase):

if __name__ == '__main__':
    unittest.main()
