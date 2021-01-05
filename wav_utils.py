from pydub import AudioSegment
import os
import beat_estimation
import crepe
import csv
import pitch_detection
import note_seq
from audio_to_midi_melodia import audio_to_midi_melodia

def trim_wav(filepath, start_time=0, end_time=-1):
    newAudio = AudioSegment.from_wav(filepath) #data/twinkle.wav"

    t1 = start_time * 1000 #Works in milliseconds
    if end_time==-1:
        newAudio = newAudio[t1:]
    else:
        t2 = end_time * 1000
        newAudio = newAudio[t1:t2]
    title = filepath.split('.')[0]
    newAudio.export(title+'_trimmed.wav', format="wav") #Exports to a wav file in the current path.

    return title+'_trimmed.wav'


def wav_to_midi(filepath, use_atmm=False, _smooth=0.25, _minduration=0.1):
      """
      Converts Wav input file into Midi
      Option to use atmm, currently false by default
      if not using atmm, does it the original way using only crepe
      """
      csv_file = filepath.split('.')[0]+'.f0.csv'
      print(csv_file, filepath)

      # Use crepe to extract frequency and confidence for each time step
      if not os.path.isfile(csv_file):
        crepe.process_file(filepath)

      frequency = []
      confidence = []
      with open(csv_file,newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
          frequency.append(float(row['frequency']))
          confidence.append(float(row['confidence']))

      # Convert into NoteSequence and do basic trimming
      seq = pitch_detection.crepe_to_note_sequenece(frequency, confidence)
      seq_to_mid = note_seq.note_sequence_to_pretty_midi(seq)

      # Extract tempo and onset estimation from midi
      estimated_tempo, estimated_start = beat_estimation.tempo_and_onset(seq_to_mid)

      # Fix Onset to start of file, set tempo, and save as Midi File
      if use_atmm:
            # When using atmm, file will be re-named with '_trimmed.mid'
            newFile = trim_wav(filepath,estimated_start)
            audio_to_midi_melodia.audio_to_midi_melodia(newFile, newFile.split('.')[0] + '.mid', estimated_tempo,
                              smooth=_smooth, minduration=_minduration)
      else:
            # When not using atmm, file will be re-named with '.mid'
            beat_estimation.quantization_and_preparation(seq,estimated_tempo, estimated_start)
            note_seq.note_sequence_to_midi_file(seq,filepath.split('.')[0] + '.mid')


if __name__=="__main__":
      wav_to_midi('data/twinkle.wav',use_atmm=False)