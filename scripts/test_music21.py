from unittest import TestCase
from music21.converter import parse
from filecmp import cmp
from random import sample
from glob import glob
from pathlib import Path
from chaotic_mapping import intervalBetween
from music21.note import Note, Chord
from music21.pitch import Pitch
from music21.stream import Stream, Voice, Part, Variant

# imports

home = str(Path.home())


class TestMusic21(TestCase):
    def test_activate_variant_tree(self):
        s1 = Stream()
        p1 = Part()
        v1 = Voice()
        v1.repeatAppend(Note("C#4"))
        p1.append(v1)
        s1.append(p1)
        var1 = Variant()
        varP1 = Part()
        varV1 = Voice()
        varV1.repeatAppend(Note("D"))
        varP1.append(varV1)
        var1.append(varP1)
        var1.groups = ["test"]
        s1.insert(0.0, var1)
        s1.activateVariants("test")
        for note in s1.parts[0].voices[0].notes:
            self.assertTrue(note.name == "D")

    def test_null_transpose(self):
        variantChord = Chord(["D", "F#", "A"])
        newPitch = Pitch("D-3")
        chordTransposeInterval = intervalBetween(variantChord, newPitch)
        print(chordTransposeInterval.name)
        self.assertTrue(chordTransposeInterval.name == "0")

    def test_octave_transpose(self):
        variantChord = Chord(["D", "F#", "A"])
        newPitch = Pitch("D-4")
        chordTransposeInterval = intervalBetween(variantChord, newPitch)
        print(chordTransposeInterval.name)
        self.assertTrue(chordTransposeInterval.name == "P8")

    def test_chord_root(self):
        variantChord = Chord(["D", "F#", "A"])
        print(variantChord.root.pitch)
        self.assertTrue(variantChord.root.pitch == "D")

    def streamAnalysis(self, midiFilename):
        stream = parse(midiFilename)
        # stream.show('text')
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
