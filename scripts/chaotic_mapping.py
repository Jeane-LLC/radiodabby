"""
chaotic_mapping.py
Arjun Iyer - Jeane LLC (c) 2021 GPL3

An implementation of Dabby '98

This script takes a MIDI file, applies a chaotic mapping, and produces a new MIDI file.

"""
from scipy.integrate import solve_ivp
from numpy import linspace
from numpy import all as NPAll
from numpy import array as NPArray
from music21.midi import MidiFile
from music21.midi import translate
from music21.stream import Stream
import argparse
from unittest import TestSuite
from unittest import TestCase
from unittest import TextTestRunner
import sys

# read a midi file
# run an ode45 for the lorenz attractor
# map the first 12 notes to the first 12 values of the ode45
# substitute those notes into the midi file
# write the new midi file with associated metadata


versionNumberString = "0.0.0"


class TestImports(TestCase):
    def test_import(self):
        self.assertTrue("scipy.integrate" in sys.modules)
        self.assertTrue("music21.midi" in sys.modules)
        return


def openMidi(filename: str):
    midifile = MidiFile.open(filename)

    return midifile


def lorenzEquations(t, V, sigma, rho, beta):
    x, y, z = V
    xDot = sigma * (y - x)
    yDot = rho * x - y - x * z
    zDot = x * y - beta * z
    return xDot, yDot, zDot


def ivpSolver(tmax: int, tn: int, rho: float, sigma: float, beta: float, V: float):
    x0, y0, z0 = V
    lorenz = solve_ivp(
        lorenzEquations,
        (0, tmax),
        (x0, y0, z0),
        args=(sigma, beta, rho),
        dense_output=True,
    )
    t = linspace(0, tmax, tn)
    x, y, z = lorenz.sol(t)
    return x, y, z


class TestLorenz(TestCase):
    def test_lorenz(self):
        x, y, z = ivpSolver(100, 1000, 0.0, 0.0, 0.0, (0.0, 0.0, 0.0))
        self.assertTrue(NPAll(NPArray([x, y, z]) == 0))


parser = argparse.ArgumentParser()
parser.add_argument(
    "-F", "--filename", help="MIDI file (.mid) to use as input", action="store_true"
)
parser.add_argument(
    "-V", "--version", help="Prints the script version number", action="store_true"
)
parser.add_argument(
    "-T",
    "--test",
    help="Runs all tests to check if script will operate as expected",
    action="store_true",
)


def testSuite():
    suite = TestSuite()
    suite.addTest(TestImports("test_import"))
    suite.addTest(TestLorenz("test_lorenz"))
    return suite


def runAllTests():
    runner = TextTestRunner()
    runner.run(testSuite())
    return


if __name__ == "__main__":
    args = parser.parse_args()

    if args.test:
        runAllTests()

    if args.version:
        print("Version " + versionNumberString)

    if args.filename:
        openMidi(args.filename)
