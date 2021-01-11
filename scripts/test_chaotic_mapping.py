from unittest import TestCase
from unittest import TextTestRunner
from unittest import TestSuite
from chaotic_mapping import getChaoticMapIndices


class TestChaoticMapping(TestCase):
    def test_empty_chaos_map(self):
        def greaterThanFilter(pair):
            return pair[0] != pair[1]

        lorenz0Vars = (10, 0.01, (1.0, 1.0, 1.0), 28.0, 10.0, 8.0 / 3)
        lorenz1Vars = (10, 0.01, (0.999, 1.0, 1.0), 28.0, 10.0, 8.0 / 3)
        chaoticMapIndices = getChaoticMapIndices(lorenz0Vars, lorenz1Vars)
        validChaoticMapIndices = filter(greaterThanFilter, chaoticMapIndices)
        TestCase.assertEqual(len(validChaoticMapIndices) == 0)  # should fail!


if __name__ == "__main__":

    def allTestsSuite():
        suite = TestSuite()
        suite.addTest(TestChaoticMapping("test_empty_chaos_map"))
        return suite

    runner = TextTestRunner()
    runner.run(allTestsSuite())
