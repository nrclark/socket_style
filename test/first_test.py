#!/usr/bin/env python

import unittest

class SimpleTestCase(unittest.TestCase):
    """Tests to ensure that the unit-test framework is working."""

    def test_does_true_work(self):
        self.assertTrue(True)

    def test_does_false_work(self):
        self.assertFalse(False)

if __name__ == '__main__':
    unittest.main()
