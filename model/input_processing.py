import os
import pretty_midi
import music21 as m21
from basic_pitch.inference import predict
from model.data_processing import encode_song

def get_midi_data(input_audio_path):
    if not os.path.exists(input_audio_path):
        raise FileNotFoundError(f"File not found: {input_audio_path}")

    _, midi_data, _ = predict(input_audio_path)
    return midi_data

def get_main_instrument(midi_data):
    if not midi_data.instruments:
        raise ValueError("There are no instruments in this file.")

    # We are assuming that the instruments with the most number of notes
    # is the main instrument, and that the rest is background noise.
    main_instrument = max(midi_data.instruments, key=lambda i: len(i.notes))

    return main_instrument

def quantize(stream, time_step=0.25):
    quantized_stream = m21.stream.Stream()

    # 1. GET ALL NOTES AND RESTS
    notes = stream.flatten().notesAndRests

    for note in notes:
        start = note.offset
        duration = note.duration.quarterLength

        quantized_start = round(start / time_step) * time_step
        quantized_duration = round(duration / time_step) * time_step

        if quantized_duration == 0:
            quantized_duration = time_step

        if isinstance(note, m21.note.Note):
            new_note = m21.note.Note(note.pitch.midi)
        else:
            new_note = m21.note.Rest()

        new_note.offset = quantized_start
        new_note.duration = m21.duration.Duration(quantized_duration)

        quantized_stream.insert(new_note)

    return quantized_stream

def filter_notes(main_instrument):
    notes = sorted(main_instrument.notes, key=lambda n: n.start)
    # Sometimes, audio picks up an extra octave sound not present
    # in the original recording, which we will filter out.
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

    filtered_instrument = pretty_midi.Instrument(
        program=main_instrument.program,
        is_drum=main_instrument.is_drum,
        name=main_instrument.name
    )

    filtered_instrument.notes = filtered_notes

    return filtered_instrument

def tranpose(stream):
    key = stream.analyze("key")

    if key.mode == "major":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == "minor":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))

    transposed_stream = stream.transpose(interval)

    return key, transposed_stream

def process_input(input_audio_path):
    # 1. GET MIDI DATA FROM AUDIO FILE
    midi_data = get_midi_data(input_audio_path)

    # We save the tempo for later audio reconstruction.
    tempo = midi_data.estimate_tempo()

    # 2. GET MAIN INSTRUMENT AND CONVERT TO MUSIC21 STREAM
    main_instrument = get_main_instrument(midi_data)
    filtered_instrument = filter_notes(main_instrument)

    stream = m21.stream.Stream()

    for note in filtered_instrument.notes:
        n = m21.note.Note(note.pitch)
        n.offset = note.start
        n.quarterLength = note.end - note.start
        stream.insert(n)

    # 3. QUANTIZE STREAM TO A 16th-note GRID
    quantized_stream = quantize(stream)

    # 4. TRANPOSE STREAM TO C/Am
    key, transposed_stream = tranpose(stream)

    encoded_song = encode_song(stream)

    return {
        "encoded_song": encoded_song,
        "tempo": tempo,
        "key": key
    }
