from unittest import TestCase
import numpy
import scipy.integrate
import music21.midi
import sys


class TestImports(TestCase):
    def test_import(self):
        self.assertTrue("scipy.integrate" in sys.modules)
        self.assertTrue("music21.midi" in sys.modules)
        self.assertTrue("numpy" in sys.modules)
        return
