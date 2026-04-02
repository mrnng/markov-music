import pretty_midi

def model_format_to_midi(model_format):
    """
    Converts from the model format to a MIDI file
    """

    pm = pretty_midi.PrettyMIDI()
    program = pretty_midi.instrument_name_to_program("Acoustic Grand Piano")
    instrument = pretty_midi.Instrument(program=program)

    tempo = model_format["tempo"]
    tonic_midi = model_format["tonic_midi"]
    notes = model_format["notes"]
    current_time = 0
    for pitch, duration in notes:
        delta_time = (duration / 4) / tempo * 60
        if pitch != 0:
            note = pretty_midi.Note(
                velocity=50,
                pitch=pitch + tonic_midi,
                start=current_time,
                end=current_time+delta_time
            )
            instrument.notes.append(note)
        current_time += delta_time
    
    pm.instruments.append(instrument)

    return pm