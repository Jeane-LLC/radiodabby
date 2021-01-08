"""
chaotic_mapping.py
Arjun Iyer - Jeane LLC (c) 2021 GPL3

An implementation of Dabby '98

This script takes a MIDI file, applies a chaotic mapping, and produces a new MIDI file.

"""
from scipy.integrate import ode
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


def testSuite():
    suite = TestSuite()
    suite.addTest(TestImports("test_import"))
    return suite


def runAllTests():
    runner = TextTestRunner()
    runner.run(testSuite())
    return


def openMidi(filename: str):
    midifile = MidiFile.open(filename)

    return midifile


def lorenzEquations(V, sigma, rho, beta):
    x, y, z = V
    xDot = sigma * (y - x)
    yDot = rho * x - y - x * z
    zDot = x * y - beta * z
    return [xDot, yDot, zDot]


def odeSolver(h: float, rho: float, sigma: float, beta: float, V: float):
    lorenz = ode(lorenzEquations).set_integrator("dopri5")
    x, y, z = V
    lorenz.set_initial_value(x, y, z).set_f_params()
    return


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

if __name__ == "__main__":
    args = parser.parse_args()

    if args.test:
        runAllTests()

    if args.version:
        print("Version " + versionNumberString)

    if args.filename:
        openMidi(args.filename)
