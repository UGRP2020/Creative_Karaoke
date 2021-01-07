from numpy.core.shape_base import atleast_1d
from pydub import AudioSegment
import os
from utils import tempo_and_onset
import crepe
import csv
import pitch_detection
import note_seq
from audio_to_midi_melodia import audio_to_midi_melodia
import visual_midi

def trim_wav(filepath, start_time=0, end_time=-1):
      """
      Cuts off the first part of the wav file
      Input: start_time is the new start time
      """
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


def wav_to_midi(filepath, use_atmm=False , outfile = None, _smooth=0.25, _minduration=0.1):
      """
      Converts Wav input file into Midi
      Option to use atmm, currently false by default
      if not using atmm, uses algorithm in pitch_detection
      """
      
      if outfile is not None:
            midi_filepath = outfile
      else:
            midi_filepath = filepath.split('.')[0] + '.mid'

      # Use crepe to extract frequency and confidence for each time step
      csv_file = 'results/crepe/'+filepath.split('/')[-1].split('.')[0]+'.f0.csv'
      if not os.path.isfile(csv_file):
        crepe.process_file(filepath,output='results/crepe')

      # Read f0.csv file
      frequency = []
      confidence = []
      with open(csv_file,newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
          frequency.append(float(row['frequency']))
          confidence.append(float(row['confidence']))

      # Convert into NoteSequence and do basic trimming
      seq = pitch_detection.crepe_to_note_sequenece(frequency, confidence, trills=True)
     
      if use_atmm:
            # Extract tempo from midi - needed as an argument for atmm
            seq_to_mid = note_seq.note_sequence_to_pretty_midi(seq)
            estimated_tempo, estimated_start = tempo_and_onset(seq_to_mid)

            # use atmm to convert wav into midi
            audio_to_midi_melodia.audio_to_midi_melodia(filepath, midi_filepath, estimated_tempo,
                              smooth=_smooth, minduration=_minduration)
      else:
            # When not using atmm, algorithm in pitch_detection will be used as default
            note_seq.note_sequence_to_midi_file(seq,midi_filepath)

      print(midi_filepath+' saved from '+filepath)


if __name__=="__main__":
      # wav 파일 녹음 한거 경로 넣어주면 같은 폴더에 [제목].mid 이름으로 미디로 변환해줌
      # 인자로 atmm == True 하면 atmm 으로 해주고 False 면 직접 짠 pitch_detection 함수들 써서 미디로 바꿔줌
      files = ['data/wav/twinkle.wav','data/wav/Letitbe.wav', 'data/wav/Hometown.wav']
      for wavfile in files:
            title = wavfile.split('/')[-1].split('.')[0]
            wav_to_midi(wavfile, outfile= 'results/test_pitch_detection/'+title+'_atmm.mid', use_atmm=True)
            wav_to_midi(wavfile, outfile= 'results/test_pitch_detection/'+title+'_no_atmm.mid', use_atmm=False)

            print('Converted wav file '+title+' into midi in results/test_pitch_detection')
