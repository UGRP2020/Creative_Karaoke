# Creative Karaoke
import note_seq
import os
from melody_generator import melody_generator
from base_generator import base_generator
from drum_generator import drum_generator
from chord_extraction import extract_roots_as_note_seq, extract_chords_from_note_sequence
from wav_utils import wav_to_midi_with_tempo
from utils import combined_sequence_to_midi_with_instruments, midi_to_wav, seq_to_midi_with_program
# from beat_analysis import 

# input 멜로디(wav)의 path 받아서 처리
def creative_karaoke(filepath, tempo=60, inst=[53, 0, 36, 118]):
    # constants
    title = filepath.split('/')[-1].split('.')[0]
    total_num_steps = 256
    outfilepath = './results/user_midi.mid'

    wav_to_midi_with_tempo(filepath, tempo, True, outfilepath) # atmm 사용 여부 선택 가능, 선택 하는 것으로 일단 작성
    user_sequence = note_seq.midi_file_to_note_sequence(outfilepath)
    user_sequence.tempos[0].qpm = tempo

    results_seq = list()

# 메인 멜로디 길이 맞춰서 뽑기
    main_melody = melody_generator(user_sequence, total_num_steps, 1.0, user_sequence.tempos[0].qpm)
    results_seq.append(main_melody)


    quantized_main_melody = note_seq.sequences_lib.quantize_note_sequence(main_melody, steps_per_quarter=4)
# 코드, 베이스, 드럼 추출
# 코드
    chords = extract_chords_from_note_sequence(quantized_main_melody)
    results_seq.append(chords)

# 베이스
    roots = extract_roots_as_note_seq(quantized_main_melody)
    base = base_generator(roots, 16, 0.7, quantized_main_melody.tempos[0].qpm)
    results_seq.append(base)

# 드럼
    sample_drum_primer = ["[(36,)]", "[(36, 42), (), (42,)]"]
    drum = drum_generator(sample_drum_primer[1], True, total_num_steps, 1.0, user_sequence.tempos[0].qpm)
    results_seq.append(drum)

# 각각 미디를 파일로 출력
    str_name_dict = {0: 'main_melody', 1: 'chords', 2: 'base', 3: 'drum'}
    combined_sequence_to_midi_with_instruments(results_seq, inst, './results/fixed/'+title+'_combined.mid')

    for i in range(len(results_seq)):
        midi = seq_to_midi_with_program(results_seq[i], inst[i])
        midi_to_wav(midi, './results/fixed/'+title+'_%s.wav' % str_name_dict[i])

if __name__== "__main__":
    folder = 'data/wav/'
    for file in os.listdir(folder):
        title = file.split('.')[0]
        bpm = int(file.split('_')[1].split('.')[0])
        creative_karaoke(folder+file,bpm)