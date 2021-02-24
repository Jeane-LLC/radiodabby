from unittest import TestCase
from chaotic_mapping import (
    getChaoticMapIndices,
    solveIVPAndOverwriteVariant,
    dabby,
    writeStreamToMidi,
    packIVPVars,
)
from music21.stream import Score, Part, Voice
from music21.note import Note, Rest
from music21.chord import Chord

nullLorenzVars = (1000, 1000, (0.0, 0.0, 0.0), 0.0, 0.0, 0.0)
lorenz0Vars = (1000, 1000, (1.0, 1.0, 1.0), 28.0, 10.0, 8.0 / 3)
lorenz1Vars = (1000, 1000, (0.999, 1.0, 1.0), 28.0, 10.0, 8.0 / 3)
lorenz2Vars = (100, 10000, (1.0, 1.0, 1.0), 28.0, 10.0, 8.0 / 3)
lorenz3Vars = (100, 10000, (0.999, 1.0, 1.0), 28.0, 10.0, 8.0 / 3)
lorenz4Vars = (5000, 5000, 1.0, 1.0, 1.0, 28.0, 10.0, 8.0 / 3)
lorenz5Vars = (5000, 5000, 0.9999, 1.0, 1.0, 28.0, 10.0, 8.0 / 3)
lorenz6Vars = (1000, 5000, (1.0, 1.0, 1.0), 28.0, 10.0, 8.0 / 3)
lorenz7Vars = (1000, 5000, (2.0, 1.0, 1.0), 28.0, 10.0, 8.0 / 3)
lorenz8Vars = (200, 200, 1.0, 1.0, 1.0, 28.0, 10.0, 8.0 / 3)
lorenz9Vars = (200, 200, 0.999, 1.0, 1.0, 28.0, 10.0, 8.0 / 3)
lorenz10Vars = (300, 300, 1.0, 1.0, 1.0, 28.0, 10.0, 8.0 / 3)
lorenz11Vars = (300, 300, 0.999, 1.0, 1.0, 28.0, 10.0, 8.0 / 3)
lorenz12Vars = (50, 50, 1.0, 1.0, 1.0, 28.0, 10.0, 8.0 / 3)
lorenz13Vars = (50, 50, 0.999, 1.0, 1.0, 28.0, 10.0, 8.0 / 3)


def greaterThanFilter(pair):
    return pair[0] != pair[1]


class TestChaoticMapping(TestCase):
    def test_dabby(self):
        filenames = [
            "~/kunstderfuge/satie/satie_gnossienne_1_(c)dery.mid",
            "~/kunstderfuge/mozart/piano/sonatas/mozart_piano_sonata_331_(hisamori).mid",
            "~/kunstderfuge/gershwin/!live!/gershwin_rhapsody_in_blue_(c)oguri.mid",
            "~/kunstderfuge/bartok/bartok_roumanian_folk_dances_3_(c)pajares.mid",
            "~/kunstderfuge/vivaldi/vivaldi_4_stagioni_primavera_1_(c)pollen.mid",
        ]
        for filename in filenames:
            stream = dabby(
                filename,
                lorenz4Vars,
                lorenz5Vars,
            )
            writeStreamToMidi(stream, filename)

    def test_solveIVPAndGenerateMixedVariant(self):
        voice1 = Voice()
        voice2 = Voice()
        mixed = [
            Note("C4", type="eighth"),
            Chord(["D4", "G4", "B4"], type="eighth"),
            Rest(type="eighth"),
            Chord(["E4", "G4", "C5"], type="eighth"),
            Note("F4", type="eighth"),
            Rest(type="eighth"),
            Rest(type="eighth"),
            Note("G4", type="eighth"),
            Rest(type="eighth"),
            Note("A4", type="eighth"),
            Chord(["B4", "D5", "G5"], type="eighth"),
            Rest(type="eighth"),
            Chord(["C5", "E5", "G5"], type="eighth"),
            Chord(["D5", "F5", "A5"], type="eighth"),
            Rest(type="eighth"),
            Rest(type="eighth"),
        ]

        for element in mixed:
            voice1.append(element)
            voice2.append(element)
        part = Part([voice1, voice2])
        score = Score([part])
        score.show("text")
        solveIVPAndOverwriteVariant(lorenz2Vars, lorenz3Vars, 9, score, "test")
        score.show("text")

    def test_solveIVPAndGenerateChordVariant(self):
        voice1 = Voice()
        voice2 = Voice()
        chordArrays = [
            ["C4", "E4", "G4"],
            ["D4", "F4", "A4"],
            ["E4", "G4", "B4"],
            ["F4", "A4", "C5"],
            ["G4", "B4", "D5"],
            ["A4", "C5", "E5"],
            ["B4", "D5", "G5"],
            ["C5", "E5", "G5"],
            ["D5", "F5", "A5"],
        ]
        for array in chordArrays:
            chord = Chord(array, type="eighth")
            voice1.append(chord)
            voice2.append(chord)
        part = Part([voice1, voice2])
        score = Score([part])
        score.show("text")
        solveIVPAndOverwriteVariant(lorenz2Vars, lorenz3Vars, 9, score, "test")
        score.show("text")

    def test_solveIVPAndGenerateNoteVariant(self):
        voice1 = Voice()
        voice2 = Voice()
        pitchStrings = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5"]
        for string in pitchStrings:
            note1 = Note(string, type="eighth")
            voice1.append(note1)
            voice2.append(Note(string, type="eighth"))
        part = Part([voice1, voice2])
        score = Score([part])
        score.show("text")
        solveIVPAndOverwriteVariant(lorenz2Vars, lorenz3Vars, 9, score, "test")
        score.show("text")

    def test_chaos_map(self):
        lorenzA, lorenzB = packIVPVars(lorenz12Vars, lorenz13Vars)
        chaoticMapIndices = getChaoticMapIndices(lorenzA, lorenzB)
        validChaoticMapIndices = list(filter(greaterThanFilter, chaoticMapIndices))
        # print(chaoticMapIndices)
        # print(validChaoticMapIndices)
        original, variant = zip(*validChaoticMapIndices)
        variantSet = set(variant)
        print("There are ~" + str(len(validChaoticMapIndices)) + " variation indices")
        print(
            "There is "
            + str(len(validChaoticMapIndices) / float(len(chaoticMapIndices)) * 100)
            + "% variation"
        )
        print(
            "The variation consists of "
            + str(len(variantSet))
            + " out of "
            + str(len(variant))
            + " indices"
        )
        self.assertFalse(len(validChaoticMapIndices) == 0)

    def test_null_chaos_map(self):
        chaoticMapIndices = getChaoticMapIndices(nullLorenzVars, lorenz0Vars)
        validChaoticMapIndices = list(filter(greaterThanFilter, chaoticMapIndices))
        print(validChaoticMapIndices)
        print("There are ~" + str(len(validChaoticMapIndices)) + " variation indices")
        self.assertTrue(len(validChaoticMapIndices) == 0)
