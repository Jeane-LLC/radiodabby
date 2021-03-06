"""
chaotic_mapping.py
Arjun Iyer - Jeane LLC (c) 2021 AGPL3

An implementation of Dabby '95

This script takes a MIDI file, applies a chaotic mapping, and produces a new MIDI file.

"""

# imports
from bisect import bisect_right
from scipy.integrate import solve_ivp
from numpy import linspace
from music21.midi import translate
from music21.converter import parse
from music21.stream import Stream
from music21.interval import Interval
from argparse import ArgumentParser
from datetime import datetime
from os.path import split
from pathlib import Path

# read a midi file
# run an ode45, l0, for the lorenz attractor with one set of initial conditions
# map the first 12 notes to the first 12 values of the ode45
# run another ode45, l1, with another set of initial conditions
# substitute those notes for each index where xi_l0 > xj_l1
# write the new midi file with associated metadata


versionNumberString = "0.0.0"
homeDir = str(Path.home())


def openMidiAsStream(filename: str):
    return parse(filename)


def writeStreamToMidi(stream: Stream, filename: str):
    variantFilename = (
        homeDir
        + "/variants/"
        + split(filename)[1].replace(
            ".mid",
            "_dabby" + "_" + datetime.now().strftime("%m%d%Y%H%M%S") + ".mid",
        )
    )
    midiFile = translate.streamToMidiFile(stream)
    midiFile.open(variantFilename, "wb")
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


def getChaoticMapIndices(lorenz0Vars, lorenz1Vars):
    tmax0, tn0, V0, rho0, sigma0, beta0 = lorenz0Vars
    tmax1, tn1, V1, rho1, sigma1, beta1 = lorenz1Vars

    lorenz0Values = ivpSolver(tmax0, tn0, V0, rho0, sigma0, beta0)
    lorenz1Values = ivpSolver(tmax1, tn1, V1, rho1, sigma1, beta1)

    # X's for pitch, Y for rhythm, Z for dynamics
    lorenz1Xs = [(i, p) for i, p in enumerate(lorenz1Values[0])]
    enumeratedLorenz0Xs = enumerate(lorenz0Values[0])
    lorenz0Xs = sorted(enumeratedLorenz0Xs, key=lambda pair: pair[1])
    return [getFirstGreaterValue(l, lorenz0Xs) for l in lorenz1Xs]


def intervalBetween(variantChord, newPitch):
    return Interval(variantChord.root().midi - newPitch.midi)


def roots(stream):
    return [extractRoot(noteOrChord) for noteOrChord in stream.notes]


def overwriteScore(score, variationIndices, numberOfPitches):
    for part in score.parts:
        rootPitches = roots(part.flat)
        effectiveNumberOfPitches = (
            len(rootPitches) if numberOfPitches == 0 else numberOfPitches
        )
        print("effectiveNumberOfPitches", effectiveNumberOfPitches)
        setRootPitches = set([pitch.nameWithOctave for pitch in rootPitches])
        print("set(rootPitches)", setRootPitches, len(setRootPitches))
        i = 0
        for noteOrChord in part.flat.notes:
            newPitch = rootPitches[variationIndices[i][1] % effectiveNumberOfPitches]
            if noteOrChord.isNote:
                noteOrChord.pitch = newPitch
            elif noteOrChord.isChord:
                midiTransposeInterval = intervalBetween(noteOrChord, newPitch)
                noteOrChord.transpose(midiTransposeInterval, inPlace=True)
            i += 1


def greaterThanFilter(pair):
    return pair[0] != pair[1]


def solveIVPAndOverwriteVariant(ivp0Vars, ivp1Vars, numberOfPitches, score, group):
    # at index j, apply pitch at index i
    chaoticMapIndices = getChaoticMapIndices(ivp0Vars, ivp1Vars)
    overwriteScore(score, chaoticMapIndices, numberOfPitches)
    return score


def packIVPVars(ivp0Vars, ivp1Vars):
    tmax0, tn0, x0, y0, z0, rho0, sigma0, beta0 = ivp0Vars
    tmax1, tn1, x1, y1, z1, rho1, sigma1, beta1 = ivp1Vars
    V0 = (x0, y0, z0)
    V1 = (x1, y1, z1)
    return (tmax0, tn0, V0, rho0, sigma0, beta0), (tmax1, tn1, V1, rho1, sigma1, beta1)


def dabby(filename: str, lorenz0: tuple, lorenz1: tuple, numberOfPitches: int = 0):
    lorenz0Vars, lorenz1Vars = packIVPVars(lorenz0, lorenz1)
    originalStream = openMidiAsStream(filename)
    return solveIVPAndOverwriteVariant(
        lorenz0Vars, lorenz1Vars, numberOfPitches, originalStream, "dabby"
    )


def getFirstGreaterValue(l: tuple, lorenz0Xs: list):
    j, x1 = l
    xValues = [x0 for _, x0 in lorenz0Xs]
    index = bisect_right(xValues, x1)
    if index - 1 > 0 and lorenz0Xs[index - 1][1] == x1:
        return (j, lorenz0Xs[index - 1][0])
    if index < len(lorenz0Xs) - 1:
        return (j, lorenz0Xs[index][0])
    return (j, j)  # Default return no variation


def extractRoot(noteOrChord):
    if noteOrChord.isNote:
        return noteOrChord.pitch
    if noteOrChord.isChord:
        return noteOrChord.root()


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument(
        "-F", "--filename", help="MIDI file (.mid) to use as input", action="store_true"
    )
    parser.add_argument(
        "-V", "--version", help="Prints the script version number", action="store_true"
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

    if args.version:
        print("Version " + versionNumberString)

    if args.filename & args.lorenz0 & args.lorenz1 & args.mapping:
        if args.mapping == "dabby":
            stream = dabby(args.filename, tuple(args.lorenz0), tuple(args.lorenz1))

            writeStreamToMidi(stream, args.filename)
            print("wrote variant")
