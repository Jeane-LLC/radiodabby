from unittest import TestCase
from music21.converter import parse
from filecmp import cmp
from random import sample
from glob import glob
from pathlib import Path
from chaotic_mapping import intervalBetween, roots, extractRoot
from music21.note import Note
from music21.chord import Chord
from music21.pitch import Pitch
from music21.stream import Voice, Part, Score
from music21.variant import Variant
from music21.interval import Interval

# imports

home = str(Path.home())


class TestMusic21(TestCase):
    def test_extract_root(self):
        note = Note("C#4", type="eighth")
        extractedPitch = extractRoot(note)
        print(
            "note.pitch",
            note.pitch,
            "extractedPitch.nameWithOctave",
            extractedPitch.nameWithOctave,
        )
        self.assertTrue(extractedPitch.nameWithOctave == "C#4")

    def test_root_pitches(self):
        v1 = Voice()
        v1.repeatAppend(Note("C#4", type="eighth"), 10)
        rootPitches = roots(v1)
        print(rootPitches)
        self.assertTrue(len(rootPitches) == 10)

    def test_activate_variant_tree(self):
        v1 = Voice()
        v1.repeatAppend(Note("C#4", type="eighth"), 10)
        p1 = Part([v1])
        sc1 = Score([p1])
        varV1 = Voice()
        varV1.repeatAppend(Note("D", type="eighth"), 10)
        varP1 = Part([varV1])
        var1 = Variant([varP1])
        var1.groups = ["test"]
        sc1.insert(0.0, var1)
        sc2 = sc1.activateVariants("test")
        sc1.show("text")
        sc2.show("text")
        for note in sc2.parts[0].voices[0].notes:
            self.assertTrue(note.name == "D")

    def test_null_transpose_note(self):
        pitch = Pitch("D4")
        nullInterval = Interval(pitch, pitch)
        print("nullInterval.name ", nullInterval.name)
        self.assertTrue(nullInterval.name == "P1")

    def test_null_transpose_chord(self):
        variantChord = Chord(["D", "F#", "A"])
        newPitch = Pitch("D4")
        chordTransposeInterval = intervalBetween(variantChord, newPitch)
        print("chordTransposeInterval.name ", chordTransposeInterval.name)
        self.assertTrue(chordTransposeInterval.name == "P1")

    def test_octave_transpose(self):
        variantChord = Chord(["D", "F#", "A"])
        newPitch = Pitch("D5")
        chordTransposeInterval = intervalBetween(variantChord, newPitch)
        print(chordTransposeInterval.name)
        self.assertTrue(chordTransposeInterval.name == "P8")

    def test_accidental_transpose(self):
        f = Pitch("F4")
        fSharp = Pitch("F#4")
        accidentalInterval = Interval(f, fSharp)
        print("accidentalInterval.name", accidentalInterval.name)
        self.assertTrue(accidentalInterval.name == "A1")

    def test_chord_root(self):
        variantChord = Chord(["D", "F#", "A"])
        print("variantChord.root()", variantChord.root())
        self.assertTrue(variantChord.root().name == "D")

    def streamAnalysis(self, midiFilename):
        stream = parse(midiFilename)
        stream.show("text")
        numberOfParts = len(stream.parts)
        numberOfVoices = 0
        for part in stream.parts:
            # part.show("text")
            print("There are " + str(len(part.voices)) + " voices")
            numberOfVoices += len(part.voices)
            for voice in part.voices:
                # voice.notesAndRests.stream().show("text")
                pass
        return stream.isFlat, numberOfParts, numberOfVoices

    def test_many_stream_consistency(self):
        # for a file in many files
        filedir = home + "/kunstderfuge/*.mid"
        numOfFiles = 100
        filePaths = glob(filedir)
        print(len(filePaths))
        filenames = sample(filePaths, numOfFiles)
        consistencyDict = {}
        for filename in filenames:
            midPath = filename
            isFlat, numberOfParts, numberOfVoices = self.streamAnalysis(midPath)
            consistencyDict[midPath] = {
                "isFlat": isFlat,
                "numberOfParts": numberOfParts,
                "numberOfVoices": numberOfVoices,
            }
        allFlats = [i["isFlat"] for i in consistencyDict]
        allNoP = [i["numberOfParts"] for i in consistencyDict]
        allNoV = [i["numberOfVoices"] for i in consistencyDict]
        allNonFlat = any(allFlats)
        lenAllNoP = len(allNoP)
        lenAllNoV = len(allNoV)
        print(
            "allNonFlat ",
            allNonFlat,
            " lenAllNoP ",
            lenAllNoP,
            " lenAllNoV ",
            lenAllNoV,
        )
        self.assertTrue(allNonFlat)
        self.assertTrue(len(allNoP) > numOfFiles)
        self.assertTrue(len(allNoV) > 2 * numOfFiles)
        # does the file have parts?
        # how many parts
        # do the parts have voices?
        # how many voices?

    def test_midi_to_stream(self):
        midiFilename = "~/kunstderfuge/satie/satie_gnossienne_1_(c)dery.mid"
        isFlat, numberOfParts, numberOfVoices = self.streamAnalysis(midiFilename)
        self.assertFalse(isFlat)

    def test_midi_to_midi(self):
        midiFilename = "/home/arjun/kunstderfuge/satie/satie_gnossienne_1_(c)dery.mid"
        stream = parse(midiFilename)
        copyOfMidiFile = stream.write(
            "midi", fp="/home/arjun/variants/satie_gnossienne_1_copy.mid"
        )
        self.assertFalse(cmp(midiFilename, copyOfMidiFile, False))
