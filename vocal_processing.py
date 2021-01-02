import note_seq
from math import log2, pow
from note_seq.protobuf import music_pb2

time_step = 0.05
A4 = 440
C0 = A4*pow(2, -4.75)

def freq_2_pitch(frequency):
  # freq should be in int form
  freq = round(frequency)
  if freq == 0: 
    return None
  h = round(12*log2(freq/C0))
  octave = h // 12
  n = h % 12
  return (octave-1)*12 + n +24  
  
def average_pitch(note_list):
  total = 0
  total_time = 0
  for note in note_list:
    duration = note.end_time - note.start_time
    total += note.pitch*duration
    total_time += duration
  return round(total/total_time)

def play_and_plot(_seq):
  note_seq.plot_sequence(_seq)
  note_seq.play_sequence(_seq,synth=note_seq.fluidsynth)

# each time step is an individual note
# filtering out ones below given confidence value
def vocal_to_NoteSequence(freq_list,conf_list,confidence=0.6):
  vocal_note_sequence = music_pb2.NoteSequence()
  for i in range(len(freq_list)):
    ptch = freq_2_pitch(freq_list[i])
    if ptch != None and conf_list[i] > confidence: # valid note
      vocal_note_sequence.notes.add(pitch = ptch, start_time = time_step*(i), end_time = time_step*(i+1), velocity = 80) 
  return vocal_note_sequence

# merges continuous notes (adjacent in time, same pitch)
def merge_continuous_notes(sequence):
  i=0
  prev_note = None
  while True:
    if i >= len(sequence.notes):
      break
    note = sequence.notes[i]
    if prev_note != None and prev_note.pitch == note.pitch and prev_note.end_time == note.start_time:
      prev_note.end_time = note.end_time
      sequence.notes.remove(note)
      continue
    prev_note = note
    i+=1

# DELETE note if it lasts for too short and is stranded from neighbors in terms of pitch
def remove_deviations(sequence, pitch_deviation=5, min_steps=2):
  i=0
  while True:
    if i >= len(sequence.notes):
      break
    note = sequence.notes[i]
    steps = round((note.end_time-note.start_time)/time_step)
    if steps <= min_steps: # assuming size of sequence.notes is greater than 1
      delete = True
      if i>0 and sequence.notes[i-1].end_time==note.start_time:
        delete = delete and (abs(sequence.notes[i-1].pitch-note.pitch)>=pitch_deviation)
      if i<len(sequence.notes)-1 and sequence.notes[i+1].start_time == note.end_time:
        delete = delete and (abs(sequence.notes[i+1].pitch-note.pitch)>=pitch_deviation)
      
      if delete: 
        sequence.notes.remove(note)
        continue  
    i+=1


def flatten_trills(sequence):
  i=0
  trills = []
  first = None
  second = None
  while True:
    if i>=len(sequence.notes):
      break
    note = sequence.notes[i]
    if len(trills)==0:
      trills.append(note)
      first = note.pitch
    else:
      if trills[len(trills)-1].end_time!=note.start_time:
        if len(trills) >=3:
          #print(trills)
          avg_ptch = average_pitch(trills)
          trills[0].pitch = avg_ptch
          trills[0].end_time = trills[len(trills)-1].end_time
          for i in range(len(trills)-1):
            sequence.notes.remove(trills[i+1])
        # clear up current trill list
        trills = [note]
        first = note.pitch
        second = None
      elif second!=None and note.pitch!=second and note.pitch!=first:
        if len(trills) >=3:
          #print(trills)
          avg_ptch = average_pitch(trills)
          trills[0].pitch = avg_ptch
          trills[0].end_time = trills[len(trills)-1].end_time
          for i in range(len(trills)-1):
            sequence.notes.remove(trills[i+1])

        if abs(trills[len(trills)-1].pitch-note.pitch)==1:
          trills = [trills[len(trills)-1],note]
          first = trills[0].pitch
          second = note.pitch
        else:
          trills = [note]
          first = note.pitch
          second = None
      elif second==None and abs(note.pitch-first)==1:
        trills.append(note)
        second=note.pitch
      elif note.pitch==second or note.pitch==first:
        trills.append(note)
    i+=1
