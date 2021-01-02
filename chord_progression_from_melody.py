from note_seq import chord_inference
from note_seq import chord_symbols_lib
from note_seq import chords_lib
from note_seq import sequences_lib
import os
import pretty_midi

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
  ## customize path here
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
      
      """
      combined = sequences_lib.concatenate_sequences([triads, seq])
      play_and_plot(combined)
      """
      break