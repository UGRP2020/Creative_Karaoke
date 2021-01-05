import pretty_midi
from note_seq import sequences_lib

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

def quantization_and_preparation(sequence, tempo, onset=False):
      # set tempo of sequence
      if len(sequence.tempos)==0:
            sequence.tempos.add()
      sequence.tempos[0].qpm = tempo

      step_per_quarter = 1
      sequence = sequences_lib.quantize_note_sequence(sequence,step_per_quarter)

      if onset != False:
        new_start_offset(sequence, onset)

def new_start_offset(sequence, onset):
    for nt in sequence.notes:
        nt.start_time -= onset
        nt.end_time -= onset
        if nt.start_time<0:
            sequence.notes.remove(nt)