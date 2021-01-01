# input: Note Sequence
# output: MIDI

from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.shared import sequence_generator_bundle
from note_seq.protobuf import generator_pb2
from note_seq.protobuf import music_pb2


def main_melody_generator(user_sequence, num_steps=128, temperature=1.0, qpm=120):
  # Melody rnn initialization
  bundle = sequence_generator_bundle.read_bundle_file('./bundle/attention_melody_rnn.mag')
  config_id = bundle.generator_details.id
  config = melody_rnn_model.default_configs[config_id]
  generator = melody_rnn_sequence_generator.MelodyRnnSequenceGenerator(model=melody_rnn_model.MelodyRnnModel(config), details=config.details, steps_per_quarter=config.steps_per_quarter, checkpoint=None, bundle=bundle)

  # Generate melody
  last_end_time = max(n.end_time for n in user_sequence.notes)
  if user_sequence.tempos and user_sequence.tempos[0].qpm:
    qpm = user_sequence.tempos[0].qpm
  seconds_per_step = 60.0 / qpm / generator.steps_per_quarter
  total_seconds = num_steps * seconds_per_step

  generator_options = generator_pb2.GeneratorOptions()
  generate_section = generator_options.generate_sections.add(start_time=last_end_time + seconds_per_step, end_time=total_seconds)

  generator_options.args['temperature'].float_value = temperature

  main_melody_sequence = generator.generate(user_sequence, generator_options)

  return main_melody_sequence










