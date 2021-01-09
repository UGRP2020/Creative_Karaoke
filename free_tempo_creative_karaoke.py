from chord_extraction import extract_chords_and_roots_from_note_sequence
from beat_analysis import wav_to_beat_annotated_sequence, midi_to_beat_annotated_sequence
from utils import combine_note_sequence_as_midi, transpose_note_sequence, seq_to_midi_with_program, midi_to_wav, combined_sequence_to_midi_with_instruments
from melody_generator import melody_generator
from note_seq.sequences_lib import quantize_note_sequence, trim_note_sequence
import note_seq
from note_seq.protobuf import music_pb2
from drum_generator import drum_generator, drum_primer
import librosa
import os
def creative_karaoke(file, inst=[53, 0, 36, 118]):
    
    title = file.split('/')[-1].split('.')[0]

    # For the free-tempo mode, beat analysis is need
    # convert input into beat-annotated note sequence 
    if file.endswith('wav'):
        # add use_atmm parameter to wav_utils function here
        user_sequence = wav_to_beat_annotated_sequence(file,use_atmm=False)
    elif file.endswith('mid'):
        user_sequence = midi_to_beat_annotated_sequence(file)
    else:
        return None

    results_seq = list()

    # extract chords and roots
    chords,roots = extract_chords_and_roots_from_note_sequence(user_sequence)
    results_seq.append(chords)

    # generate additional melody
    # specify num
    main_melody = melody_generator(user_sequence, temperature = 0.5)
    
    # generate bassline using roots
    quantized_roots = quantize_note_sequence(roots, steps_per_quarter = 4)

    grace_steps = 3
    bass = melody_generator(quantized_roots, temperature = 1.0, num_steps = quantized_roots.total_quantized_steps+grace_steps)
    transpose_note_sequence(bass, -2)
    
    # drums    
    primer = drum_primer(quantized_roots)
    drums = drum_generator(primer, temperature = 2.0, num_steps = quantized_roots.total_quantized_steps*2)
    drums = trim_note_sequence(drums, bass.total_time,drums.total_time)
    for nt in drums.notes:
        nt.start_time -= bass.total_time
        nt.end_time -= bass.total_time

    results_seq = [user_sequence, chords, bass]

    str_name_dict = {0: 'main_melody', 1: 'chords', 2: 'base', 3: 'drum'}
    combined_sequence_to_midi_with_instruments(results_seq, inst[0:3], './results/free/'+title+'_combined.mid')

    for i in range(len(results_seq)):
        midi = seq_to_midi_with_program(results_seq[i], inst[i])
        midi_to_wav(midi, './results/free/'+title+'_%s.wav' % str_name_dict[i])

if __name__=="__main__":
    folder = 'data/wav/'
    for file in os.listdir(folder):
        creative_karaoke(folder+file)