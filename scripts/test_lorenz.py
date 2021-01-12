from unittest import TestCase
from numpy import all as NPAll
from numpy import array as NPArray
from chaotic_mapping import ivpSolver


class TestLorenz(TestCase):
    def test_null_lorenz(self):
        x, y, z = ivpSolver(100, 1000, (0.0, 0.0, 0.0), 0.0, 0.0, 0.0)
        self.assertTrue(NPAll(NPArray([x, y, z]) == 0)
