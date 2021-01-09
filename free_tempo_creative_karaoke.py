from chord_extraction import extract_chords_and_roots_from_note_sequence
from beat_analysis import wav_to_beat_annotated_sequence, midi_to_beat_annotated_sequence
from utils import combine_note_sequence_as_midi, transpose_note_sequence
from melody_generator import melody_generator
from note_seq.sequences_lib import quantize_note_sequence
import note_seq
from note_seq.protobuf import music_pb2
from fixed_tempo_drum_generator import drum_generator

def creative_karaoke(filepath):
    # input files
    files = ['data/wav/twinkle.wav','data/wav/Hometown.wav','data/midi/RadioActive.mid']
    for file in files:
        title = file.split('/')[-1].split('.')[0]

        # For the free-tempo mode, beat analysis is need
        # convert input into beat-annotated note sequence 
        if file.endswith('wav'):
            # add use_atmm parameter to wav_utils function here
            user_sequence = wav_to_beat_annotated_sequence(file,use_atmm=False)
        elif file.endswith('mid'):
            user_sequence = midi_to_beat_annotated_sequence(file)
        else:
            continue

        results_seq = list()

        # extract chords and roots
        chords,roots = extract_chords_and_roots_from_note_sequence(user_sequence)
        results_seq.append(chords)

        # generate additional melody
        #main_melody = melody_generator(user_sequence,)
        
        # generate bassline using roots
        quantized_roots = quantize_note_sequence(roots, steps_per_quarter = 4)

        grace_steps = 3
        bass = melody_generator(quantized_roots, temperature = 1.0, num_steps = quantized_roots.total_quantized_steps+grace_steps)
        transpose_note_sequence(bass, -2)
        
        # drums
        drum_primer = [()]*(quantized_roots.total_quantized_steps+grace_steps)
        for nt in quantized_roots.notes:
            drum_primer[nt.quantized_start_step] = (40,)
        print(str(drum_primer))
        drums = drum_generator(str(drum_primer), temperature= 3.0, num_steps = quantized_roots.total_quantized_steps+grace_steps)
        
        result_folder = 'results/test_free_tempo/'
        combine_note_sequence_as_midi([drums],result_folder+title+'drums.mid')
        #combine_note_sequence_as_midi([roots],'not_quantized.mid')
        #combined = combine_note_sequence_as_midi(results_seq,result_folder+title+'.mid')

if __name__=="__main__":
    creative_karaoke('')