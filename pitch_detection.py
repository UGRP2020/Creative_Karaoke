import note_seq
from math import log2, pow
from note_seq.protobuf import music_pb2
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

# each time step is an individual note
# filtering out ones below given confidence value
def vocal_to_NoteSequence(freq_list,conf_list,confidence=0.6):
  vocal_note_sequence = music_pb2.NoteSequence()
  for i in range(len(freq_list)):
    ptch = freq_2_pitch(freq_list[i])
    if ptch != None and conf_list[i] > confidence: # valid note
      vocal_note_sequence.notes.add(pitch = ptch, start_time = time_step*(i), end_time = time_step*(i+1), velocity = 80) 
  return vocal_note_sequence