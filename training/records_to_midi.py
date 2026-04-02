import tensorflow as tf
import pretty_midi

filenames = [
    f"Records/validation_pitchseq-0000{i}-of-00008.tfrecord" for i in range(2, 5)
]

raw_dataset = tf.data.TFRecordDataset(filenames)

context_features = {
    "toussaint": tf.io.FixedLenFeature([], tf.float32, default_value=0.0),
    "note_density": tf.io.FixedLenFeature([], tf.float32, default_value=0.0),
}

sequence_features = {
    "pitch_seq": tf.io.FixedLenSequenceFeature([64], tf.int64)
}

def parse_fn(serialized_example):
    context, sequence = tf.io.parse_single_sequence_example(
        serialized_example,
        context_features=context_features,
        sequence_features=sequence_features
    )
    return context, sequence

parsed_dataset = raw_dataset.map(parse_fn)

counter = 0
for context, sequence in parsed_dataset:

    pitch_seq = tf.squeeze(sequence["pitch_seq"], axis=0).numpy()

    pm = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0)

    step = 0.25  # assume 16th notes
    current_note = None
    start_time = 0
    time = 0

    for token in pitch_seq:
        if token <= 127:
            # end previous note if exists
            if current_note is not None:
                instrument.notes.append(
                    pretty_midi.Note(
                        velocity=80,
                        pitch=current_note,
                        start=start_time,
                        end=time
                    )
                )
            current_note = int(token)
            start_time = time

        elif token == 128:
            # rest → close note if active
            if current_note is not None:
                instrument.notes.append(
                    pretty_midi.Note(
                        velocity=80,
                        pitch=current_note,
                        start=start_time,
                        end=time
                    )
                )
                current_note = None

        elif token == 129:
            # sustain → do nothing, just extend time
            pass

        time += step

    # close last note if still active
    if current_note is not None:
        instrument.notes.append(
            pretty_midi.Note(
                velocity=80,
                pitch=current_note,
                start=start_time,
                end=time
            )
        )

    pm.instruments.append(instrument)
    pm.write(f"Records_to_MIDI/output-test-{counter}.mid")

    counter += 1