from unittest import TestCase
from chaotic_mapping import getChaoticMapIndices, solveIVPAndGenerateVariant
from music21.stream import Score, Part, Voice
from music21.note import Note
from music21.chord import Chord

nullLorenzVars = (1000, 1000, (0.0, 0.0, 0.0), 0.0, 0.0, 0.0)
lorenz0Vars = (1000, 1000, (1.0, 1.0, 1.0), 28.0, 10.0, 8.0 / 3)
lorenz1Vars = (1000, 1000, (0.999, 1.0, 1.0), 28.0, 10.0, 8.0 / 3)


def greaterThanFilter(pair):
    return pair[0] != pair[1]


class TestChaoticMapping(TestCase):
    def test_solveIVPAndGenerateVariant(self):
        voice = Voice()
        pitchStrings = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
        for string in pitchStrings:
            voice.append(Note(string, type="eighth"))
        part = Part([voice])
        score = Score([part])
        solveIVPAndGenerateVariant(lorenz0Vars, lorenz1Vars, 9, score, "test")
        variantScore = score.activateVariants("test")
        variantScore.show("text")

    def test_chaos_map(self):
        chaoticMapIndices = getChaoticMapIndices(lorenz0Vars, lorenz1Vars)
        validChaoticMapIndices = list(filter(greaterThanFilter, chaoticMapIndices))
        print(validChaoticMapIndices)
        print("There are ~" + str(len(validChaoticMapIndices)) + " valid indices")
        self.assertFalse(len(validChaoticMapIndices) == 0)

    def test_null_chaos_map(self):
        chaoticMapIndices = getChaoticMapIndices(nullLorenzVars, lorenz0Vars)
        validChaoticMapIndices = list(filter(greaterThanFilter, chaoticMapIndices))
        print(validChaoticMapIndices)
        print("There are ~" + str(len(validChaoticMapIndices)) + " valid indices")
        self.assertTrue(len(validChaoticMapIndices) == 0)
