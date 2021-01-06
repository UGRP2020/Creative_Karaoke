from note_seq.protobuf import music_pb2
from note_seq import sequences_lib
import note_seq
import pretty_midi

import utils

def tempo_and_onset(midi_data, integer_tempo=True, steps_per_quarter=1):
    """
    Extracts tempo and onset(start time of first estimated beat) of the given midi data
        using functionality provided by pretty_midi

    Returns: tempo in qpm (float)
             onset in start time (seconds) of first estimated beat
    """
    tempo = midi_data.estimate_tempo()
    onset_beat = midi_data.estimate_beat_start()
    steps_per_second = steps_per_quarter*tempo/60
    onset_time = onset_beat/steps_per_second

    if integer_tempo:
        tempo = int(tempo)

    return tempo, onset_time

"""
def quantization_and_preparation(sequence, tempo, onset=False):
      # set tempo of sequence
      if len(sequence.tempos)==0:
            sequence.tempos.add()
      sequence.tempos[0].qpm = tempo

      # hyperparameter
      step_per_quarter = 1
      sequence = sequences_lib.quantize_note_sequence(sequence,step_per_quarter)

      if onset != False:
        adjust_sequence_to_onset(sequence, onset)
"""

def set_tempo(sequence, tempo):
    """
    Sets tempo of sequence
    """
    if len(sequence.tempos)==0:
        sequence.tempos.add()
    sequence.tempos[0].qpm = tempo

def adjust_sequence_to_onset(sequence, onset):
    """
    Moves sequence by onset (in seconds), adjusting the start of the song
    """
    for nt in sequence.notes:
        nt.start_time -= onset
        nt.end_time -= onset
        if nt.start_time<0:
            sequence.notes.remove(nt)
    print('moving sequence by %s seconds',onset)

def convert_beat_annotation_to_note_sequence(sequence, beat_pitch = None):
    """
    Converts text annotations within note sequence into a separate note sequence
    """
    seq = music_pb2.NoteSequence()

     # default pitch of beat set to C3
    if beat_pitch is None:
        beat_pitch = pretty_midi.note_name_to_number('C3')
    """
    if len(sequence.key_signatures) !=0:
        beat_pitch = sequence.key_signatures[0].keys()
    """
    for ta in sequence.text_annotations:
        if ta.annotation_type == music_pb2.NoteSequence.TextAnnotation.BEAT:
            seq.notes.add(pitch=beat_pitch, start_time = ta.time, end_time = ta.time+0.5,velocity = 80 if ta.quantized_step % 4==1 else 40)

    return seq

def seconds_per_beat(tempo):
    return 60/tempo

def add_beat_annotations(sequence):
    """
    Adds beat annotations according to tempo information stored in sequence
    Input: sequence needs to have tempo set before entering this function,
        assumes sequence is already adjusted according to detected onset
    """
    if len(sequence.tempos)==0:
        # cannot apply beat extraction
        print('tempo is not set in input sequence, returning None')
        return None

    sec_per_beat = seconds_per_beat(sequence.tempos[0].qpm)
    
    time = 0
    count = 1
    while time<sequence.total_time:
        ta = sequence.text_annotations.add()
        ta.time= time+0.00001 # time starts just above zero
        ta.annotation_type = music_pb2.NoteSequence.TextAnnotation.BEAT
        ta.quantized_step = count # quantized_step starts with 1
        time += sec_per_beat
        count +=1

def midi_to_sequence(filepath, beat_analysis = True):
    """
    Converts a midi file into a note sequence and adds beat annotations according to estimated tempo and onset
    """
    if not filepath.endswith('.mid') and not filepath.endswith('.midi'):
        print('cannot convert non midi file')
        return None

    mid = pretty_midi.PrettyMIDI(filepath)
    seq = note_seq.midi_to_note_sequence(mid)

    # get tempo and onset (midi format)
    tempo, start_time = tempo_and_onset(mid)
    if beat_analysis:
        # set tempo and move file to start @ onset (note sequence now)
        adjust_sequence_to_onset(seq,start_time)
        set_tempo(seq,tempo)

        # add beat annotations (to note sequence)
        add_beat_annotations(seq)
    
    return seq

if __name__=="__main__":
    folder = 'data/midi/'
    files = ['PianoMan.mid']
    for file in files:
        filepath = folder+file
        seq = midi_to_sequence(filepath)
        beat_seq = convert_beat_annotation_to_note_sequence(seq)

        # combine beats with melody
        midpath = 'results/mid/beats_combined_no_adjustment.mid'
        utils.combine_note_sequence_as_midi([beat_seq, seq],midpath)