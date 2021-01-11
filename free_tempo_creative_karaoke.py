from chord_extraction import extract_chords_and_roots_from_note_sequence
from utils import combine_note_sequence_as_midi, transpose_note_sequence, seq_to_midi_with_program, midi_to_wav, combined_sequence_to_midi_with_instruments
from melody_generator import melody_generator
from note_seq.sequences_lib import quantize_note_sequence, trim_note_sequence
import note_seq
from note_seq.protobuf import music_pb2
from drum_generator import drum_generator, drum_primer
import os
import pretty_midi
from constant import *

from beat_analysis import wav_to_beat_annotated_sequence, midi_to_beat_annotated_sequence

def creative_karaoke(file, genre = GENRE_JAZZ, velocity = [80,50,60,90]):
    total_num_steps = 256

    title = file.split('/')[-1].split('.')[0]
    inst = genre_inst[genre]
    vocal_mid_file = 'vocal_converted_to_midi.mid'
    # For the free-tempo mode, beat analysis is need
    # convert input into beat-annotated note sequence 
    if file.endswith('wav'):
        # add use_atmm parameter to wav_utils function here
        user_sequence = wav_to_beat_annotated_sequence(file, True, True, vocal_mid_file)
    elif file.endswith('mid'):
        user_sequence = midi_to_beat_annotated_sequence(file)
    else:
        return None

    midi_data = pretty_midi.PrettyMIDI(vocal_mid_file)
    estimated_tempo = midi_data.estimate_tempo()

    # generate main melody
    main_melody = melody_generator(user_sequence, total_num_steps, 0.5, estimated_tempo)

    # extract chords and roots
    chords,roots = extract_chords_and_roots_from_note_sequence(user_sequence, maj_min = True, triads = (genre!=GENRE_JAZZ), _chords_per_bar=None)
     
    # generate bassline using roots
    quantized_roots = quantize_note_sequence(roots, steps_per_quarter = 4)

    bass = melody_generator(quantized_roots, temperature = 1.0, num_steps = total_num_steps)
    transpose_note_sequence(bass, -2)
    
    # drums    
    primer = drum_primer(quantized_roots)
    drums = drum_generator(primer, temperature = 1.0, num_steps = total_num_steps)
    #drums = trim_note_sequence(drums, bass.total_time,drums.total_time)
    """for nt in drums.notes:
        nt.start_time -= bass.total_time
        nt.end_time -= bass.total_time
    """
    results_seq = [main_melody, chords, bass, drums]

    str_name_dict = {0: 'main_melody', 1: 'chords', 2: 'base', 3: 'drum'}
    combined_sequence_to_midi_with_instruments(results_seq, inst, velocity, './results/free/'+title+'_combined.mid')

    for i in range(len(results_seq)):
        midi = seq_to_midi_with_program(results_seq[i], inst[i],velocity[i], is_drum=(i==3))
        midi_to_wav(midi, './results/free/'+title+'_%s.wav' % str_name_dict[i])

if __name__=="__main__":
    folder = 'data/wav/130/'
    genre = GENRE_JAZZ
    for file in os.listdir(folder):
        creative_karaoke(folder+file)