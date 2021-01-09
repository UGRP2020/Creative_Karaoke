import note_seq
from note_seq import sequences_lib
from note_seq.protobuf import music_pb2
import pretty_midi
import visual_midi
from midi2audio import FluidSynth
import os

def play_and_plot(_seq):
  """
  Works only in Google colab
  """
  note_seq.plot_sequence(_seq)
  note_seq.play_sequence(_seq,synth=note_seq.fluidsynth)

def seq_to_midi_with_program(sequence, program_number):
      midi_with_program = pretty_midi.PrettyMIDI()
      inst = pretty_midi.Instrument(program=program_number)
      for nt in sequence.notes:
            note = pretty_midi.Note(velocity = nt.velocity,pitch = nt.pitch,start = nt.start_time, end = nt.end_time)
            inst.notes.append(note)
      midi_with_program.instruments.append(inst)

      return midi_with_program

def midi_to_wav(midi_data, filepath):
      tmp_midi_file = 'temp.mid'
      midi_data.write(tmp_midi_file)
      FluidSynth().midi_to_audio(tmp_midi_file,filepath)
      os.remove(tmp_midi_file)


def combine_note_sequence_as_midi(sequences,filepath):
      """
      Combines multiple note sequences into a midi file

      Arguments: sequences is a list of note sequences
                filepath is name of path you wish to store midi file
      """
      default_program = 0
      combined = pretty_midi.PrettyMIDI()
      for seq in sequences:
            # save sequences as individual INSTRUMENTS in PrettyMIDI format
            if len(seq.notes)!=0:
                  program_number = seq.notes[0].program
            else:
                  program_number = default_program

            inst = pretty_midi.Instrument(program=program_number)
            for nt in seq.notes:
                  note = pretty_midi.Note(velocity = nt.velocity,pitch = nt.pitch,start = nt.start_time, end = nt.end_time)
                  inst.notes.append(note)

            combined.instruments.append(inst)
      combined.write(filepath)
      save_plot(filepath)
      #print(str(len(sequences))+' sequences combined and saved as '+filepath)


def save_plot(filepath):
      """
      Saves a plot of the midi file
      Arguments: filepath is the name of the midifile to save
      """
      if not filepath.endswith('mid') and not filepath.endswith('midi'):
            print('Cannot save plot for non-midi files')
            return
      folder = 'results/plot/'
      midi = pretty_midi.PrettyMIDI(filepath)
      plotter = visual_midi.Plotter()
      plotter.show(midi,folder+filepath.split('/')[-1].partition('.')[0]+'.html')


def tempo_and_onset(midi_data, integer_tempo=True, steps_per_quarter=4):
    """
    Extracts tempo and onset(start time of first estimated beat) of the given midi data
        using functionality provided by pretty_midi

    Returns: tempo in qpm (float)
             onset in start time (seconds) of first estimated beat
    """
    tempo = midi_data.estimate_tempo()
    onset_beat = midi_data.estimate_beat_start()
    steps_per_second = steps_per_quarter*tempo/60
    onset_time = onset_beat/steps_per_second

    if integer_tempo:
        tempo = int(tempo)

    return tempo, onset_time

# NOTE: Changed to Fixed Tempo version
def get_onset(midi_data, tempo, steps_per_quarter=4):
    """
    Extracts tempo and onset(start time of first estimated beat) of the given midi data
        using functionality provided by pretty_midi

    Returns: tempo in qpm (float)
             onset in start time (seconds) of first estimated beat
    """
    onset_beat = midi_data.estimate_beat_start()
    steps_per_second = steps_per_quarter*tempo/60
    onset_time = onset_beat/steps_per_second

    return onset_time
    
def transpose_note_sequence(sequence, octave):
      """Transposes all notes in sequence by input octave"
      Input: octave in integers ex. 1, -1 etc.
      """
      transpose_pitch = octave*12
      for nt in sequence.notes:
            nt.pitch += transpose_pitch

      

