from unittest import TestCase
from music21.stream import Stream
from music21.converter import parse
from music21.midi.translate import streamToMidiFile
from filecmp import cmp
from random import sample
from os import listdir, path
from glob import glob
from pathlib import Path

# imports

home = str(Path.home())


class TestMusic21(TestCase):
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
