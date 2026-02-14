import os
from basic_pitch.inference import predict
from pretty_midi import note_number_to_name

DURATION_TABLE = [
    (4.0, "whole"),
    (2.0, "half"),
    (1.0, "quarter"),
    (0.5, "eighth"),
    (0.333, "quarter-triplet"),
    (0.25, "sixteenth"),
    (0.1667, "eighth-triplet"),
    (0.125, "thirty-second"),
]

def get_midi_data(audio_filepath):
    """
    Returns MIDI data from audio file as a PrettyMIDI object.
    """
    if not os.path.exists(audio_filepath):
        raise FileNotFoundError(f"File not found: {audio_filepath}")

    _, midi_data, _ = predict(audio_filepath)
    return midi_data

def quantize(time_in_quarters):
    """
    Helper function that returns the nearest name for a duration
    """
    return min(DURATION_TABLE, key=lambda x: abs(x[0] - time_in_quarters))

def midi_to_model_format(midi_data):
    model_format = {}
    tempo = midi_data.estimate_tempo()
    model_format["tempo"] = tempo
    quarter_in_seconds = 60 / tempo
    # extract the main instrument, which is the one with most notes
    # our audio files will be monophonic, so this should always work
    main_instrument = max(midi_data.instruments, key=lambda i: len(i.notes))
    notes = sorted(main_instrument.notes, key=lambda n: n.start)

    durations = []
    current_time = notes[0].start
    for note in notes:
        rest_length = note.start - current_time
        if rest_length >= quarter_in_seconds:
            _, rest_name = quantize(rest_length / quarter_in_seconds)
            durations.append(("rest", rest_name))

        note_length = note.end - note.start
        _, note_name = quantize(note_length / quarter_in_seconds)
        durations.append((note_number_to_name(note.pitch), note_name))

        current_time = max(current_time, note.end)

    model_format["durations"] = durations

    return model_format

def model_format_to_midi(model_format):
    pass