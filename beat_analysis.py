from note_seq.protobuf import music_pb2
import note_seq
import pretty_midi
import utils
from midi2audio import FluidSynth
from aubio import tempo, source
import os
from wav_utils import wav_to_midi



def convert_beat_annotation_to_note_sequence(sequence, beat_pitch = None):
    """
    Converts text annotations (of type BEAT) within note sequence into a separate note sequence
    May be used for debugging beat estimation
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
            seq.notes.add(pitch=beat_pitch, start_time = ta.time, end_time = ta.time+0.5,velocity = 100 if ta.quantized_step % 4==1 else 40)

    return seq

def seconds_per_beat(tempo):
    return 60/tempo


def get_beats(filename):
    """Returns a list of seconds a beat is detected
    These beats will be added as beat annotations in a note sequence

    Uses the AUBIO library, this code was copied and pasted from demo_tempo.py
    """
    win_s = 512                 # fft size
    hop_s = win_s // 2          # hop size

    samplerate = 0

    s = source(filename, samplerate, hop_s)
    samplerate = s.samplerate
    o = tempo("default", win_s, hop_s, samplerate)

    # tempo detection delay, in samples
    # default to 4 blocks delay to catch up with
    delay = 4. * hop_s

    # list of beats, in samples
    beats = []

    # total number of frames read
    total_frames = 0
    while True:
        samples, read = s()
        is_beat = o(samples)
        if is_beat:
            this_beat = int(total_frames - delay + is_beat[0] * hop_s)
            #print("%f" % (this_beat / float(samplerate)))
            beats.append(this_beat / float(samplerate))
        total_frames += read
        if read < hop_s: break
    
    return beats

def add_beat_annotations(sequence, beats):
    """Adds beat information as text_annotations in input sequence
    """
    for beat in beats:
        ta = sequence.text_annotations.add()
        ta.annotation_type = music_pb2.NoteSequence.TextAnnotation.BEAT
        ta.time = float(beat)

def wav_to_beat_annotated_sequence(filename):
    if not filename.endswith('.wav'):
        print('file must be wav file')
        return None

    # Convert Wav to Midi file to convert to note sequence
    tmp_mid_file = filename.split('.')[0]+'_tmp.mid'
    wav_to_midi(filename,use_atmm=True,outfile=tmp_mid_file)

    seq = note_seq.midi_file_to_note_sequence(tmp_mid_file)

    # Beat Extraction using AUBIO library
    # note that input file may be actual voice recording instead of a midi-converted-wav file
    beats = get_beats(filename)
    add_beat_annotations(seq,beats)
    
    # Delete temporary mid file
    os.remove(tmp_mid_file)

    return seq

def wav_to_beat_annotated_sequence(filename, use_atmm = False):
    if not filename.endswith('.wav'):
        print('file must be wav file')
        return None

    # Convert Wav to Midi file to convert to note sequence
    tmp_mid_file = filename.split('.')[0]+'_tmp.mid'
    wav_to_midi(filename,use_atmm=use_atmm,outfile=tmp_mid_file)

    seq = note_seq.midi_file_to_note_sequence(tmp_mid_file)

    # Beat Extraction using AUBIO library
    # note that input file may be actual voice recording instead of a midi-converted-wav file
    beats = get_beats(filename)
    add_beat_annotations(seq,beats)
    
    # Delete temporary mid file
    os.remove(tmp_mid_file)

    return seq

def midi_to_beat_annotated_sequence(filename):
    """Converts a midi file into a note sequence with annotated beats"""
    if not filename.endswith('.mid'):
        print('file must be midi file')
        return None

    # Convert Midi to wav file to extract beats (uses midi2audio library)
    tmp_wav_file = filename.split('.')[0]+'.wav'
    FluidSynth().midi_to_audio(filename,tmp_wav_file)
    
    seq = note_seq.midi_file_to_note_sequence(filename)

    # Beat extraction using AUBIO library
    beats = get_beats(tmp_wav_file)
    add_beat_annotations(seq,beats)

    # Delete temporary wav file
    os.remove(tmp_wav_file)

    return seq

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

"""
def add_beat_annotations(sequence):
    
    #Adds beat annotations according to tempo information stored in sequence
    #Input: sequence needs to have tempo set before entering this function,
    #    assumes sequence is already adjusted according to detected onset
    
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
    
    #Converts a midi file into a note sequence and adds beat annotations according to estimated tempo and onset
    
    if not filepath.endswith('.mid') and not filepath.endswith('.midi'):
        print('cannot convert non midi file')
        return None

    mid = pretty_midi.PrettyMIDI(filepath)
    seq = note_seq.midi_to_note_sequence(mid)

    if beat_analysis:
        # get tempo and onset (midi format)
        tempo, start_time = tempo_and_onset(mid)

        # set tempo and move file to start @ onset (note sequence now)
        adjust_sequence_to_onset(seq,start_time)
        set_tempo(seq,tempo/2)
        
        # add beat annotations (to note sequence)
        add_beat_annotations(seq)
    
    return seq

def txt_to_list(filename):
    with open(filename) as f:
        content = f.readlines()
    content = [x.strip() for x in content] 
    return content
"""


if __name__=="__main__":
    files = ['data/midi/RadioActive.mid','data/midi/September.mid','data/wav/twinkle.wav','data/wav/Letitbe.wav', 'data/wav/Hometown.wav']
    for file in files:
        if file.endswith('.wav'):
            seq = wav_to_beat_annotated_sequence(file)
        elif file.endswith('.mid'):
            seq = midi_to_beat_annotated_sequence(file)
        else:
            continue

        beat_seq = convert_beat_annotation_to_note_sequence(seq)
        
        midpath = 'results/test_beat_analysis/'+file.split('/')[-1].split('.')[0]+'.mid'
        utils.combine_note_sequence_as_midi([beat_seq,seq],midpath)

        print('Combined estimated beat and melody for '+file+' in results/test_beat/analysis')