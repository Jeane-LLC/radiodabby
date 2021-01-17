from unittest import TestCase
from music21.stream import Stream
from music21.converter import parse
from music21.midi.translate import streamToMidiFile
from filecmp import cmp


class TestMusic21(TestCase):
    def test_midi_to_stream(self):
        midiFilename = "~/kunstderfuge/satie/satie_gnossienne_1_(c)dery.mid"
        stream = parse(midiFilename)
        # stream.show('text')
        for part in stream.parts:
            # part.show("text")
            print("There are " + str(len(part.voices)) + " voices")
            for voice in part.voices:
                # voice.notesAndRests.stream().show("text")
                pass
        self.assertFalse(stream.isFlat)

    def test_midi_to_midi(self):
        midiFilename = "/home/arjun/kunstderfuge/satie/satie_gnossienne_1_(c)dery.mid"
        stream = parse(midiFilename)
        copyOfMidiFile = stream.write(
            "midi", fp="/home/arjun/variants/satie_gnossienne_1_copy.mid"
        )
        self.assertTrue(cmp(midiFilename, copyOfMidiFile, False))
