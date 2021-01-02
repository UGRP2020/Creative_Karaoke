# Base generator

import ast

from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.shared import sequence_generator_bundle
from note_seq.protobuf import generator_pb2
from note_seq.protobuf import music_pb2
from note_seq.sequences_lib import concatenate_sequences
from note_seq import Melody
from melody_generator import melody_generator

def base_generator(roots_sequence, num_steps=16, temperature=0.5, qpm=120, chords_per_bar=1):
    base_sequences_list = list()
    for n in roots_sequence.notes:
        for i in range(chords_per_bar):
            root_melody = Melody(ast.literal_eval("[" + str(n.pitch - 12) +"]"))
            root_sequence = root_melody.to_sequence(qpm=qpm)
            base_chunk = melody_generator(root_sequence, num_steps, temperature, qpm)
            base_sequences_list.append(base_chunk)
        
    base_sequence = concatenate_sequences(base_sequences_list)
    return base_sequence






    
