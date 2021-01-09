import ast

from magenta.models.drums_rnn import drums_rnn_model
from magenta.models.drums_rnn import drums_rnn_sequence_generator
from magenta.models.shared import sequence_generator
from magenta.models.shared import sequence_generator_bundle
import note_seq
from note_seq.protobuf import generator_pb2
from note_seq.protobuf import music_pb2
import tensorflow.compat.v1 as tf

HIGH_TOM = 50
BASS_DRUM = 36
ACOUSTIC_SNARE = 38
HIGH_HAT = 42

def drum_generator(primer, is_primer_seq=True, num_steps=256, temperature=1.0, qpm=120):
    bundle = sequence_generator_bundle.read_bundle_file('./bundle/drum_kit_rnn.mag')
    config_id = bundle.generator_details.id
    config = drums_rnn_model.default_configs[config_id]

    generator = drums_rnn_sequence_generator.DrumsRnnSequenceGenerator(
      model=drums_rnn_model.DrumsRnnModel(config),
      details=config.details,
      steps_per_quarter=config.steps_per_quarter,
      checkpoint=None,
      bundle=bundle)

    seconds_per_step = 60.0 / qpm / generator.steps_per_quarter
    total_seconds = num_steps * seconds_per_step

    generator_options = generator_pb2.GeneratorOptions()

    primer_seq = music_pb2.NoteSequence()
    if is_primer_seq: # When primer is sequence
        primer_drums = note_seq.DrumTrack([
        frozenset(pitches) for pitches in ast.literal_eval(primer)
        ])
        primer_seq = primer_drums.to_sequence(qpm=qpm)
    else: # When primer is midi
        primer_seq = note_seq.midi_file_to_sequence_proto(primer)

    generator_options = generator_pb2.GeneratorOptions()
    
    # Set the start time to begin on the next step after the last note ends.
    if primer_seq.notes:
        last_end_time = max(n.end_time for n in primer_seq.notes)
    else:
        last_end_time = 0
    generate_section = generator_options.generate_sections.add(
        start_time=last_end_time + seconds_per_step,
        end_time=total_seconds)

    if generate_section.start_time >= generate_section.end_time:
        tf.logging.fatal(
            'Priming sequence is longer than the total number of steps '
            'requested: Priming sequence length: %s, Generation length '
            'requested: %s',
            generate_section.start_time, total_seconds)
        return

    generator_options.args['temperature'].float_value = temperature
    drum = generator.generate(primer_seq, generator_options)

    return drum

def drum_primer(beats):
    grace_steps = 3
    drum_primer = [()]*(beats.total_quantized_steps+grace_steps)

    count=0
    for nt in beats.notes:
        if count==0:
            drum_primer[nt.quantized_start_step] = (BASS_DRUM, ACOUSTIC_SNARE, HIGH_HAT,)
        elif count==2:
            drum_primer[nt.quantized_start_step] = (ACOUSTIC_SNARE, HIGH_HAT,)
        else:
            drum_primer[nt.quantized_start_step] = (HIGH_HAT,)
        count = (count+1)%4
    
    return str(drum_primer)
    
if __name__ == "__main__":
    drum = drum_generator("[(36,)]")
    note_seq.sequence_proto_to_midi_file(drum, 'test_drum_generator.mid')