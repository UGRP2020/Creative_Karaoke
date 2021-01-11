# Creative Karaoke
import note_seq
import os
from melody_generator import melody_generator
from base_generator import base_generator
from drum_generator import drum_generator
from chord_extraction import extract_roots_as_note_seq, extract_chords_from_note_sequence, extract_chords_and_roots_from_note_sequence
from wav_utils import wav_to_midi_with_tempo
from utils import combined_sequence_to_midi_with_instruments, midi_to_wav, seq_to_midi_with_program, transpose_note_sequence
from note_seq.sequences_lib import stretch_note_sequence
from constant import *

# input 멜로디(wav)의 path 받아서 처리
# melody, chords, bass, drums [100,53,35,40] 18
genre_inst = {GENRE_JAZZ:[65,0,36,40],GENRE_DISCO:[54,53,36,40],GENRE_CLASSICAL:[40,48,43,61], GENRE_ROCK:[29,5,34,0]}
genre_drum = {GENRE_JAZZ:"120 Bossa Hihat.mid",GENRE_DISCO:"130 DISCOA.mid",GENRE_CLASSICAL:"120 Bossa Hihat.mid", GENRE_ROCK:"70 Ridebell sync groove.mid"}
genre_str = {GENRE_JAZZ:"Jazz",GENRE_DISCO:"Disco",GENRE_CLASSICAL:"Classical", GENRE_ROCK:"Rock"}

def creative_karaoke(filepath, tempo=60, genre = GENRE_JAZZ, velocity = [80,50,90,90]):
    # constants
    total_num_steps = 256
    outfilepath = './results/user_midi.mid'

    title = filepath.split('/')[-1].split('.')[0]
    inst = genre_inst[genre]
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
    chords, roots = extract_chords_and_roots_from_note_sequence(quantized_main_melody, maj_min=True, triads=(genre != GENRE_JAZZ))
    results_seq.append(chords)

# 베이스
    bass = base_generator(roots, 16, 0.7, quantized_main_melody.tempos[0].qpm)
    #transpose_note_sequence(bass, 1)
    results_seq.append(bass)

# 드럼
    if genre is not GENRE_CLASSICAL:
        """
        for file in os.listdir('data/drum_rhythm/'):
            drum = drum_generator('data/drum_rhythm/'+file, is_primer_seq=False, num_steps = total_num_steps, temperature=1.0, qpm = user_sequence.tempos[0].qpm)
            break
        """   
        drumpath = 'data/drum_rhythm/' + genre_drum[genre]
        name = genre_drum[genre].split('.')[0]
        tempo = int(name.split(' ')[0])
        factor = user_sequence.tempos[0].qpm / tempo
        print('tempo is %s, factor is %s' % (tempo, factor))

        drum_seq = note_seq.midi_file_to_note_sequence(drumpath)
        stretched_seq = stretch_note_sequence(drum_seq,factor)
        temp_file = 'tmp_stretched_drum.mid'
        note_seq.note_sequence_to_midi_file(stretched_seq, temp_file)

        drum = drum_generator(temp_file, is_primer_seq=False, num_steps = total_num_steps, temperature=1.0, qpm = user_sequence.tempos[0].qpm)
        os.remove(temp_file)
        results_seq.append(drum)
    else: 
        results_seq.append(roots)
        velocity = [90,50,50,50]

# 각각 미디를 파일로 출력
    str_name_dict = {0: 'main_melody', 1: 'chords', 2: 'base', 3: 'drum'}
    combined_sequence_to_midi_with_instruments(results_seq, inst, velocity,'./results/fixed/%s_%s.mid'% (genre_str[genre], title), genre)

    for i in range(len(results_seq)):
        midi = seq_to_midi_with_program(results_seq[i], inst[i],velocity[i],is_drum = (genre != GENRE_CLASSICAL and i==3))
        midi_to_wav(midi, './results/fixed/%s_%s_%s.wav' % (title, genre_str[genre], str_name_dict[i]))

if __name__== "__main__":
    genre = GENRE_JAZZ
    tempo = genre_drum[genre].split(" ")[0]
    folder = 'data/wav/%s/' % tempo
    for file in os.listdir(folder):
        title = file.split('.')[0]
        # bpm = int(file.split('_')[1].split('.')[0])
        creative_karaoke(folder+file, int(tempo), genre)