import os
import pretty_midi
from basic_pitch.inference import predict

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
    """
    Converts to the format used for the Markov model, which is:
    {
        tempo: float,
        notes: [(name, duration)]
    }
    """
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

    # sometimes, audio picks up an extra octave sound not present
    # in the original recording, which we will filter
    filtered_notes = []
    i = 0
    while i < len(notes) - 1:
        if abs(notes[i].start - notes[i+1].start) < 0.1:
            note_i = pretty_midi.note_number_to_name(notes[i].pitch)
            note_j = pretty_midi.note_number_to_name(notes[i+1].pitch)
            if note_i[:-1] == note_j[:-1]:
                note_to_keep = i if int(note_i[-1]) < int(note_j[-1]) else i + 1
                filtered_notes.append(notes[note_to_keep])
                i += 2
                continue
        filtered_notes.append(notes[i])
        i += 1

    for note in filtered_notes:
        rest_length = note.start - current_time
        if rest_length >= quarter_in_seconds:
            _, rest_name = quantize(rest_length / quarter_in_seconds)
            durations.append(("rest", rest_name))

        note_length = note.end - note.start
        _, duration_name = quantize(note_length / quarter_in_seconds)
        note_name = pretty_midi.note_number_to_name(note.pitch)
        durations.append((note_name, duration_name))

        current_time = max(current_time, note.end)

    model_format["notes"] = durations

    return model_format

def model_format_to_midi(model_format):
    """
    Converts from the model format to a MIDI file
    """
    # a lookup table for duration names
    durations_lut = {name: duration for duration, name in DURATION_TABLE}

    pm = pretty_midi.PrettyMIDI()
    program = pretty_midi.instrument_name_to_program("Acoustic Grand Piano")
    instrument = pretty_midi.Instrument(program=program)

    tempo = model_format["tempo"]
    notes = model_format["notes"]
    current_time = 0
    for note_name, duration_name in notes:
        delta_time = durations_lut[duration_name] / tempo * 60
        if note_name != "rest":
            note_number = pretty_midi.note_name_to_number(note_name)
            note = pretty_midi.Note(
                velocity=50,
                pitch=note_number,
                start=current_time,
                end=current_time+delta_time
            )
            instrument.notes.append(note)
        current_time += delta_time
    
    pm.instruments.append(instrument)

    return pm