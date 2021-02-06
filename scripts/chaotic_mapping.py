"""
chaotic_mapping.py
Arjun Iyer - Jeane LLC (c) 2021 AGPL3

An implementation of Dabby '95

This script takes a MIDI file, applies a chaotic mapping, and produces a new MIDI file.

"""

# imports
from music21.stream import Part
from music21.stream import Voice
from bisect import bisect_right
from scipy.integrate import solve_ivp
from numpy import linspace
from music21.midi import translate
from music21.converter import parse
from music21.stream import Stream
from music21.variant import Variant
from music21.interval import Interval
from argparse import ArgumentParser
from copy import deepcopy
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


def writeStreamVariantToMidi(stream: Stream, group: str, filename: str):
    variantFilename = (
        homeDir
        + "/variants/"
        + split(filename)[1].replace(
            ".mid",
            "_dabby" + "_" + datetime.now().strftime("%m%d%Y%H%M%S") + ".mid",
        )
    )
    variantStream = stream.activateVariants(group)
    midiFile = translate.streamToMidiFile(variantStream)
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


def roots(voice):
    return [extractRoot(noteOrChord) for noteOrChord in voice.notes]


def generateVariantPartAndVoice(
    score, variant, voiceIndex, variationIndices, numberOfPitches
):
    for part in score.parts:
        if len(part.voices) < 1:
            break
        voice = part.voices[voiceIndex]
        rootPitches = roots(voice)
        variantVoice = Voice()
        p = 0
        for generalNoteSubclass in voice.notesAndRests:
            if p > numberOfPitches - 1:
                p = 0
            if variationIndices[p][1] < len(rootPitches):
                newPitch = rootPitches[variationIndices[p][1]]
                variation = True
            else:
                variation = False
            if generalNoteSubclass.isNote:
                variantNote = deepcopy(generalNoteSubclass)
                if variation:
                    variantNote.pitch = newPitch
                variantVoice.append(
                    variantNote
                )  # a copy of the note with the appropriate pitch
                p += 1
            elif generalNoteSubclass.isChord:
                midiTransposeInterval = intervalBetween(generalNoteSubclass, newPitch)
                if variation:
                    variantChord = generalNoteSubclass.transpose(midiTransposeInterval)
                variantVoice.append(variantChord)
                p += 1
            elif generalNoteSubclass.isRest:
                variantVoice.append(generalNoteSubclass)
        variantPart = Part([variantVoice])
        variant.append(variantPart)


def greaterThanFilter(pair):
    return pair[0] != pair[1]


def solveIVPAndGenerateVariant(ivp0Vars, ivp1Vars, numberOfPitches, score, group):
    # at index j, apply pitch at index i
    chaoticMapIndices = getChaoticMapIndices(ivp0Vars, ivp1Vars)
    variant = Variant()
    generateVariantPartAndVoice(score, variant, 0, chaoticMapIndices, numberOfPitches)
    generateVariantPartAndVoice(score, variant, 1, chaoticMapIndices, numberOfPitches)
    generateVariantPartAndVoice(score, variant, 2, chaoticMapIndices, numberOfPitches)
    variant.groups = [group]
    score.insert(0.0, variant)
    return score


def dabby(filename: str, lorenz0: tuple, lorenz1: tuple, numberOfPitches: int = 0):
    tmax0, tn0, x0, y0, z0, rho0, sigma0, beta0 = lorenz0
    tmax1, tn1, x1, y1, z1, rho1, sigma1, beta1 = lorenz1
    V0 = (x0, y0, z0)
    V1 = (x1, y1, z1)
    originalStream = openMidiAsStream(filename)
    lorenz0Vars = (tmax0, tn0, V0, rho0, sigma0, beta0)
    lorenz1Vars = (tmax1, tn1, V1, rho1, sigma1, beta1)

    return solveIVPAndGenerateVariant(
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

            writeStreamVariantToMidi(stream, "dabby", args.filename)
            print("wrote variant")
