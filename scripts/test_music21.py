from unittest import TestCase
from music21.stream import Stream
from music21.converter import parse
from music21.midi.translate import streamToMidiFile


class TestMusic21(TestCase):
    def test_midi_to_stream(self):
        midiFilename = "~/kunstderfuge/satie/satie_gnossienne_1_(c)dery.mid"
        stream = parse(midiFilename)
        # stream.show('text')
        for part in stream.parts:
            # part.show("text")
            print("There are " + str(len(part.voices)) + " voices")
            for voice in part.voices:
                voice.notesAndRests.stream().show("text")
                pass
        self.assertFalse(stream.isFlat)
