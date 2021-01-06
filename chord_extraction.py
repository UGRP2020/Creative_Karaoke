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

    """
	duration = 4*60/sequence.tempos[0].qpm
	if major_minor:
		for chord in sequence.text_annotations:
			if chord.annotation_type == chords_lib.CHORD_SYMBOL:
				chord_pitches = chord_symbols_lib.chord_symbol_pitches(chord.text)
				# leave only major / minor chords and ignore the rest
				if chord_symbols_lib.chord_symbol_quality(chord.text) >1:
					continue
				count = 0
				for note in chord_pitches:
					if inversion:
						if note<chord_pitches[0]:
							note+=12
					if count<3:
						chords.notes.add(pitch=note+60,start_time=chord.time, end_time = chord.time+duration,velocity = 40)
					count+=1
	elif triads:
		for chord in sequence.text_annotations:
			if chord.annotation_type == chords_lib.CHORD_SYMBOL:
				chord_pitches = chord_symbols_lib.chord_symbol_pitches(chord.text)
				count = 0
				for note in chord_pitches:
					if inversion:
						if note<chord_pitches[0]:
							note+=12
					if count<3:
						chords.notes.add(pitch=note+60,start_time=chord.time, end_time = chord.time+duration,velocity = 40)
					count+=1
	else:
		for chord in sequence.text_annotations:
			if chord.annotation_type == chords_lib.CHORD_SYMBOL:
				chord_pitches = chord_symbols_lib.chord_symbol_pitches(chord.text)
				for note in chord_pitches:
					if inversion:
						if note<chord_pitches[0]:
							note+=12
						chords.notes.add(pitch=note+60,start_time=chord.time, end_time = chord.time+duration,velocity = 40)

	return chords
	"""


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


""" 
def melody_and_chords(seq, onset_detection = True):
	# get estimated tempo of melody and set as qpm
		estimated_tempo = midi_data.estimate_tempo()
		print('estimated tempo is '+str(estimated_tempo))
		seq.tempos[0].qpm = estimated_tempo
		
		# quantize melody note sequence, with one step per quarter
		step_per_quarter = 1
		seq = sequences_lib.quantize_note_sequence(seq,step_per_quarter)

		if onset_detection:
			onset = midi_data.estimate_beat_start()
			# print('start beat is '+str(onset))
			steps_per_second = seq.quantization_info.steps_per_quarter * seq.tempos[0].qpm/60
			onset_time = onset*1/steps_per_second
	
			for nt in seq.notes:
				nt.start_time -= onset_time
				nt.end_time -= onset_time
				if nt.start_time<0:
					seq.notes.remove(nt)

		print('Main Melody')
		play_and_plot(seq)
		# extract chords from quantized sequence
		chords = extract_chords_as_note_seq(seq)
		print('Melody and Chords Played Together')
		combined = sequences_lib.concatenate_sequences([chords, seq])
		play_and_plot(combined)


	 
def extract_chords_as_note_seq(sequence,triads = True):
	chords = music_pb2.NoteSequence()

	# this needs to be adjusted
	sequence.quantization_info.steps_per_quarter = 4

	sequence.total_quantized_steps = 120
	try:
		chord_inference.infer_chords_for_sequence(sequence)
	except chord_inference.SequenceAlreadyHasChordsError:
		nothing = 1

	if triads == True:
		for chord in sequence.text_annotations:
			if chord.annotation_type == chords_lib.CHORD_SYMBOL:
				chord_pitches = chord_symbols_lib.chord_symbol_pitches(chord.text)
				count = 0
				for note in chord_pitches:
					if count<3:
						chords.notes.add(pitch=note+60,start_time=chord.time, end_time = chord.time+1,velocity = 80)
					count+=1
	else:
		for chord in sequence.text_annotations:
			if chord.annotation_type == chords_lib.CHORD_SYMBOL:
				chord_pitches = chord_symbols_lib.chord_symbol_pitches(chord.text)
				for note in chord_pitches:
						chords.notes.add(pitch=note+60,start_time=chord.time, end_time = chord.time+1,velocity = 80)
					
	return chords


def extract_roots_as_note_seq(sequence):
	roots = music_pb2.NoteSequence()

	 # this needs to be adjusted
	sequence.quantization_info.steps_per_quarter = 4

	sequence.total_quantized_steps = 120
	try:
		chord_inference.infer_chords_for_sequence(sequence)
	except chord_inference.SequenceAlreadyHasChordsError:
		nothing = 1

	# collect only the first note in the chord symbol (the root)
	for chord in sequence.text_annotations:
		if chord.annotation_type == chords_lib.CHORD_SYMBOL:
			chord_pitches = chord_symbols_lib.chord_symbol_pitches(chord.text)
			for note in chord_pitches:
				roots.notes.add(pitch=note+60,start_time=chord.time, end_time = chord.time+1,velocity = 80)
				break
				
	return roots


def get_chords_and_roots():
	# customize path here
	vocal_path = 'drive/MyDrive/vocal_input/'
	for file in os.listdir(vocal_path):
		filepath = vocal_path + file
		if file.endswith('.mid'):
			# opening trimmed vocal file saved as midi format into NoteSequence
			midi_data = pretty_midi.PrettyMIDI(filepath)
			seq = note_seq.midi_to_note_sequence(midi_data)
			
			chords = extract_chords_as_note_seq(seq)
			roots = extract_roots_as_note_seq(seq)

			pm_chords = note_seq.note_sequence_to_pretty_midi(chords)
			pm_roots = note_seq.note_sequence_to_pretty_midi(roots)
			pm_melody = note_seq.note_sequence_to_pretty_midi(seq)

			print(pm_chords)
			print(pm_chords.instruments)
			print(pm_melody.estimate_tempo())
			pm_chords.instruments[0].program = 42
			
			
			break
"""
