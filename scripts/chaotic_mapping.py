"""
chaotic_mapping.py
Arjun Iyer - Jeane LLC (c) 2021 GPL3

An implementation of Dabby '95

This script takes a MIDI file, applies a chaotic mapping, and produces a new MIDI file.

"""

# imports
from scipy.integrate import solve_ivp
from numpy import linspace
from numpy import all as NPAll
from numpy import array as NPArray
from music21.midi import translate
from music21.converter import parse
from music21.stream import Stream
from music21.variant import Variant
from music21.note import Note
from music21.chord import Chord
from music21.interval import Interval
from argparse import ArgumentParser
from unittest import TestSuite
from unittest import TestCase
from unittest import TextTestRunner
import sys
from copy import deepcopy
from datetime.datetime import now
from os.path import split
from pathlib.Path import home

# read a midi file
# run an ode45, l0, for the lorenz attractor with one set of initial conditions
# map the first 12 notes to the first 12 values of the ode45
# run another ode45, l1, with another set of initial conditions
# substitute those notes for each index where xi_l0 > xj_l1
# write the new midi file with associated metadata


versionNumberString = "0.0.0"
homeDir = str(home())


class TestImports(TestCase):
    def test_import(self):
        self.assertTrue("scipy.integrate" in sys.modules)
        self.assertTrue("music21.midi" in sys.modules)
        return


def openMidiAsStream(filename: str):
    return parse(filename)


def writeStreamVariantToMidi(stream: Stream, group: str, filename: str):
    stream.activateVariants(group)
    midiFile = translate.streamToMidiFile(stream)
    midiFile.open(filename, "wb")
    midiFile.write()
    midiFile.close()


def lorenzEquations(t, V, sigma, rho, beta):
    x, y, z = V
    xDot = sigma * (y - x)
    yDot = rho * x - y - x * z
    zDot = x * y - beta * z
    return xDot, yDot, zDot


def ivpSolver(tmax: int, tn: int, V: float, rho: float, sigma: float, beta: float):
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


def getChaoticMapIndices(lorenz0Vars, lorenz1Vars):
    tmax0, tn0, V0, rho0, sigma0, beta0 = lorenz0Vars
    tmax1, tn1, V1, rho1, sigma1, beta1 = lorenz1Vars

    lorenz0Values = ivpSolver(tmax0, tn0, V0, rho0, sigma0, beta0)
    lorenz1Values = ivpSolver(tmax1, tn1, V1, rho1, sigma1, beta1)

    # X's for pitch, Y for rhythm, Z for dynamics

    lorenz0Xs = [(i, p[0]) for i, p in enumerate(lorenz0Values)]
    lorenz1Xs = [(i, p[0]) for i, p in enumerate(lorenz1Values)]
    lorenz0Xs.sort(key=lambda x: x[1])
    return [mapping(l, lorenz0Xs) for l in lorenz1Xs]


def dabby(filename: str, lorenz0: tuple, lorenz1: tuple, numberOfPitches: int = 0):
    tmax0, tn0, x0, y0, z0, rho0, sigma0, beta0 = lorenz0
    tmax1, tn1, x1, y1, z1, rho1, sigma1, beta1 = lorenz1
    V0 = (x0, y0, z0)
    V1 = (x1, y1, z1)
    originalStream = openMidiAsStream(filename)
    rootPitches = [extractRoot(noteOrChord) for noteOrChord in originalStream.notes]
    lorenz0Vars = (tmax0, tn0, V0, rho0, sigma0, beta0)
    lorenz1Vars = (tmax1, tn1, V1, rho1, sigma1, beta1)
    if numberOfPitches == 0:
        numberOfPitches = len(rootPitches)
    # at index j, apply pitch at index i
    variationIndices = getChaoticMapIndices(lorenz0Vars, lorenz1Vars)
    variant = Variant()

    p = 0
    for generalNoteSubclass in originalStream.notesAndRests:
        if p > numberOfPitches - 1:
            break
        newPitch = rootPitches[variationIndices[p][1]]

        if generalNoteSubclass.isNote:
            variantNote = deepcopy(generalNoteSubclass)
            variantNote.pitch = newPitch
            variant.append(variantNote)  # a copy of the note with the appropriate pitch
            p += 1
        elif generalNoteSubclass.isChord:
            variantChord = deepcopy(generalNoteSubclass)
            midiTransposeInterval = Interval(
                variantChord.root.pitch.midi - newPitch.midi
            )
            variantChord.transpose(midiTransposeInterval)
            variant.append(
                variantChord
            )  # a copy of the chord transposed by the detla between root & new pitch
            p += 1
        elif generalNoteSubclass.isRest:
            variant.append(generalNoteSubclass)

    variant.groups = ["dabby"]
    originalStream.insert(0.0, variant)
    return originalStream


def mapping(l: tuple, lorenz0Xs: list):
    j, x1 = l
    for i, x0 in lorenz0Xs:
        if x0 > x1:
            return (j, i)
    return (j, j)  # Default return no variation


def extractRoot(noteOrChord):
    if noteOrChord is Note:
        return noteOrChord.pitch
    if noteOrChord is Chord:
        return noteOrChord.root()


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

    parser = ArgumentParser()
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

    parser.add_argument(
        "-L0",
        "--lorenz0",
        help="Parameters to map to the original midi file",
        action="store_true",
    )

    parser.add_argument(
        "-L1",
        "--lorenz1",
        help="Parameters to generate the variant midi file",
        action="store_true",
    )

    parser.add_argument(
        "-M",
        "--mapping",
        help="The name of the mapping strategy to apply",
        action="store_true",
    )

    args = parser.parse_args()

    if args.test:
        runAllTests()

    if args.version:
        print("Version " + versionNumberString)

    if args.filename & args.lorenz0 & args.lorenz1 & args.mapping:
        if args.mapping == "dabby":
            stream = dabby(args.filename, tuple(args.lorenz0), tuple(args.lorenz1))
            newFilename = (
                homeDir
                + "/variants/"
                + split(args.filename)[1].replace(
                    ".mid", "_dabby" + "_" + now.strftime("%m%d%Y%H%M%S") + ".mid"
                )
            )
            writeStreamVariantToMidi(stream, "dabby", newFilename)
            print("wrote " + newFilename)
