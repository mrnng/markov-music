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

    # this is the actual note to format step
    for note in filtered_notes:
        rest_steps = max(0, round((note.start - current_time) / step_duration))
        if rest_steps > 0:
            events.append((0, rest_steps))
        duration_steps = max(1, round((note.end - note.start) / step_duration))
        events.append((note.pitch, duration_steps))
        current_time = note.start + duration_steps * step_duration

    model_format["notes"] = events

    return model_format

def model_format_to_midi(model_format):
    """
    Converts from the model format to a MIDI file
    """

    pm = pretty_midi.PrettyMIDI()
    program = pretty_midi.instrument_name_to_program("Acoustic Grand Piano")
    instrument = pretty_midi.Instrument(program=program)

    tempo = model_format["tempo"]
    notes = model_format["notes"]
    current_time = 0
    for pitch, duration in notes:
        delta_time = (duration / 4) / tempo * 60
        if pitch != 0:
            note = pretty_midi.Note(
                velocity=50,
                pitch=pitch,
                start=current_time,
                end=current_time+delta_time
            )
            instrument.notes.append(note)
        current_time += delta_time
    
    pm.instruments.append(instrument)

    return pm

def test_pipeline(audio_filepath):
    midi_data = get_midi_data(audio_filepath)
    model_format = midi_to_model_format(midi_data)
    output_midi = model_format_to_midi(model_format)
    return output_midi