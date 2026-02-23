# TODO:
# add key detection and convert notes in the model_format to scale degrees

import os
import pretty_midi
from basic_pitch.inference import predict

def get_midi_data(audio_filepath):
    """
    Returns MIDI data from audio file as a PrettyMIDI object.
    """
    if not os.path.exists(audio_filepath):
        raise FileNotFoundError(f"File not found: {audio_filepath}")

    _, midi_data, _ = predict(audio_filepath)
    return midi_data

import numpy as np

def detect_key_from_histogram(histogram):
    """
    A simple implementation of the Krumhansl-Schmuckler key-finding algorithm.
    The histogram should contain the durations of notes in the order below (NOTE_NAMES).
    """
    MAJOR_PROFILE = np.array([
        6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
        2.52, 5.19, 2.39, 3.66, 2.29, 2.8
    ])

    MINOR_PROFILE = np.array([
        6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
        2.54, 4.75, 3.98, 2.69, 3.34, 3.17
    ])

    NOTE_NAMES = np.array([
        "C", "C#", "D", "D#", "E", "F",
        "F#", "G", "G#", "A", "A#", "B"
    ])

    if histogram.sum() == 0:
        return None

    histogram = histogram / histogram.sum()

    best_score = -np.inf
    best_key = None

    for i in range(12):
        major_rot = np.roll(MAJOR_PROFILE, i)
        minor_rot = np.roll(MINOR_PROFILE, i)

        major_score = np.corrcoef(histogram, major_rot)[0, 1]
        minor_score = np.corrcoef(histogram, minor_rot)[0, 1]

        if major_score > best_score:
            best_score = major_score
            best_key = f"{NOTE_NAMES[i]}-major"

        if minor_score > best_score:
            best_score = minor_score
            best_key = f"{NOTE_NAMES[i]}-minor"

    return best_key

def midi_to_model_format(midi_data):
    """
    Converts to the format used for the Markov model, which is:
    {
        tempo: float,
        notes: [(pitch, duration)]
    }
    """
    model_format = {}
    tempo = midi_data.estimate_tempo()
    model_format["tempo"] = tempo
    quarter_in_seconds = 60 / tempo
    # we divide by 4 because we're on a 16th note grid
    step_duration = quarter_in_seconds / 4
    # extract the main instrument, which is the one with most notes
    # our audio files will be monophonic, so this should always work
    main_instrument = max(midi_data.instruments, key=lambda i: len(i.notes))
    notes = sorted(main_instrument.notes, key=lambda n: n.start)

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

    # if there are no notes, avoid crashing
    if len(filtered_notes) == 0:
        model_format["notes"] = []
        return model_format

    # this is the actual note to format step
    events = []
    current_time = round(filtered_notes[0].start / step_duration) * step_duration
    for note in filtered_notes:
        rest_steps = max(0, round((note.start - current_time) / step_duration))
        if rest_steps > 0:
            events.append((0, rest_steps))
        duration_steps = max(1, round((note.end - note.start) / step_duration))
        events.append((note.pitch, duration_steps))
        current_time = note.start + duration_steps * step_duration

    model_format["notes"] = events

    return model_format
