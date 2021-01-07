from note_seq import chord_inference
from note_seq import chord_symbols_lib
from note_seq.chord_symbols_lib import chord_symbol_pitches, chord_symbol_quality, chord_symbol_root, CHORD_QUALITY_MINOR, CHORD_QUALITY_MAJOR
from note_seq import chords_lib
from note_seq.sequences_lib import is_quantized_sequence, quantize_note_sequence
from note_seq import music_pb2
import note_seq
import pretty_midi
import os

from beat_analysis import midi_to_sequence, convert_beat_annotation_to_note_sequence
from utils import combine_note_sequence_as_midi


def convert_chords_annotation_to_note_sequence(sequence, maj_min=True, triads=True, inversion=False):
    """
    Converts text annotations (of type CHORD_SYMBOL) within note sequence into a separate note sequence
    MAJ_MIN is enabled when extracting only major and minor chords (dismissing other types)
    TRIADS is enabled when extracting triads of the originally estimated chords
    INVERSION is disabled when pitches are positioned in ascending order according to R, 3, 5
    """
    seq = music_pb2.NoteSequence()

    # how long a bar lasts
    duration = 4*60/sequence.tempos[0].qpm

    # indicates which octave chords will be placed at (pitch class must be C)
    start_offset = pretty_midi.note_name_to_number('C4')

    # get only chord annotations in the sequence (for beat annotations, refer to convert_beat_annotation_to_note_sequence() beat_analysis)
    chord_annotations = [ta for ta in sequence.text_annotations if ta.annotation_type ==
                         music_pb2.NoteSequence.TextAnnotation.CHORD_SYMBOL]

    for i in range(len(chord_annotations)):
        ta = chord_annotations[i]

        # if chord is something other than a major or minor, skip!
        if maj_min and (chord_symbol_quality(ta.text) > CHORD_QUALITY_MINOR):
            continue

        # select only three notes (root, 3rd, 5th) if in triad mode
        if triads:
            chord_pitches = chord_symbol_pitches(ta.text)[0:3]
        else:
            chord_pitches = chord_symbol_pitches(ta.text)

        # end time of chord will be until the start of the next chord annotation
        if i == (len(chord_annotations)-1):
            end = ta.time+duration
        else:
            end = chord_annotations[i+1].time

        for ptch in chord_pitches:
            if not inversion:
                if ptch < chord_pitches[0]:
                    ptch += 12
            seq.notes.add(pitch=ptch+start_offset, start_time=ta.time,
                          end_time=end, velocity=60)

    return seq


def extract_chords_from_note_sequence(sequence, major_minor=True, triads=True, inversion=False, _chords_per_bar=1):
    """
    Extracts chords from note sequence

    Input sequence must be quantized
    Returns a note sequence with chords for each bar
    """
    if not is_quantized_sequence(sequence):
        # quantization needed
        steps_per_quarter = 4
        sequence = quantize_note_sequence(sequence, 4)

    try:
        chord_inference.infer_chords_for_sequence(
            sequence, chords_per_bar=_chords_per_bar)
    except chord_inference.SequenceAlreadyHasChordsError:
        nothing = 1

    chords = convert_chords_annotation_to_note_sequence(sequence)
    return chords


def extract_roots_as_note_seq(sequence, _chords_per_bar=1):
    roots = music_pb2.NoteSequence()

    try:
        chord_inference.infer_chords_for_sequence(
            sequence, chords_per_bar=_chords_per_bar)
    except chord_inference.SequenceAlreadyHasChordsError:
        nothing = 1

    duration = 4*60/sequence.tempos[0].qpm
    # collect only the first note in the chord symbol (the root)
    for chord in sequence.text_annotations:
        if chord.annotation_type == chords_lib.CHORD_SYMBOL:
            chord_pitches = chord_symbols_lib.chord_symbol_pitches(chord.text)
            for note in chord_pitches:
                roots.notes.add(pitch=note+60, start_time=chord.time,
                                end_time=chord.time+duration, velocity=80)
                break

    return roots


if __name__ == "__main__":
    folder = 'data/midi/'
    files = ['PianoMan.mid']
    for file in files:
        filepath = folder+file
        seq = midi_to_sequence(filepath)
        chords = extract_chords_from_note_sequence(seq)

        midpath = 'results/mid/chords_and_melody.mid'
        combine_note_sequence_as_midi([seq, chords], midpath)
