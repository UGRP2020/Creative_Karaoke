import note_seq

def play_and_plot(_seq):
  note_seq.plot_sequence(_seq)
  note_seq.play_sequence(_seq,synth=note_seq.fluidsynth)
