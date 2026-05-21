import os
import math
import pretty_midi
import music21 as m21
from basic_pitch.inference import predict

def encode_song(song, time_step=0.25):
    # Map-based approach ensures every event is processed and nothing is skipped.
    # We call stream() to avoid StreamIteratorInefficientWarning.
    flat_song = song.flatten().notesAndRests.stream()
    if not flat_song:
        return ""

    steps_map = {}
    # Sort by offset to ensure later notes correctly handle overlaps.
    # If offsets are equal, higher pitch wins for the melody.
    events = sorted(flat_song, key=lambda e: (e.offset, getattr(e, 'pitch', m21.pitch.Pitch(0)).midi))
    
    for event in events:
        start_step = int(round(event.offset / time_step))
        duration_steps = int(round(event.duration.quarterLength / time_step))
        if duration_steps < 1:
            duration_steps = 1
            
        symbol = str(event.pitch.midi) if isinstance(event, m21.note.Note) else "r"
        
        # Place note start
        steps_map[start_step] = symbol
        
        # Place sustains
        for s in range(start_step + 1, start_step + duration_steps):
            # Only fill if nothing else has started here
            if s not in steps_map:
                steps_map[s] = "_"
    
    if not steps_map:
        return ""
        
    max_step = max(steps_map.keys())
    raw_encoded = []
    last_event_symbol = None
    for i in range(max_step + 1):
        val = steps_map.get(i, "r")
        if val == "r":
            if raw_encoded and (raw_encoded[-1] == "r" or (raw_encoded[-1] == "_" and last_event_symbol == "r")):
                raw_encoded.append("_")
            else:
                raw_encoded.append("r")
        else:
            raw_encoded.append(val)

        if val != "_":
            last_event_symbol = val
            
    # Post-process to enforce power-of-2 durations (no dotted notes or ties)
    encoded_song = []
    i = 0
    while i < len(raw_encoded):
        symbol = raw_encoded[i]
        length = 1
        j = i + 1
        while j < len(raw_encoded) and raw_encoded[j] == "_":
            length += 1
            j += 1
        
        # Largest power of 2 <= length (1, 2, 4, 8, 16...)
        new_length = 2 ** int(math.log2(length))
        
        encoded_song.append(symbol)
        for _ in range(new_length - 1):
            encoded_song.append("_")
        # Fill truncation gaps with rests
        for _ in range(length - new_length):
            encoded_song.append("r")
            
        i = j
            
    return " ".join(encoded_song)

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
    notes = sorted(stream.flatten().notesAndRests, key=lambda n: n.offset)
    
    # Valid power-of-2 step lengths
    VALID_STEPS = [1, 2, 4, 8, 16]

    for i, note in enumerate(notes):
        start = float(note.offset)
        duration = float(note.duration.quarterLength)

        quantized_start = round(start / time_step) * time_step
        
        # Round duration to nearest valid power-of-2 steps
        target_steps = duration / time_step
        if target_steps < 1:
            power_of_2_steps = 1
        else:
            # Find the closest value in VALID_STEPS
            power_of_2_steps = min(VALID_STEPS, key=lambda x: abs(x - target_steps))
            
        quantized_duration = power_of_2_steps * time_step

        # Prevent overlap with the next note
        if i < len(notes) - 1:
            next_start = float(notes[i+1].offset)
            quantized_next_start = round(next_start / time_step) * time_step
            if quantized_start + quantized_duration > quantized_next_start:
                # Reduce duration to fit before the next note
                max_allowed_steps = int((quantized_next_start - quantized_start) / time_step)
                if max_allowed_steps >= 1:
                    # Find largest valid power-of-2 steps that fits
                    fitting_steps = [s for s in VALID_STEPS if s <= max_allowed_steps]
                    power_of_2_steps = max(fitting_steps) if fitting_steps else 1
                    quantized_duration = power_of_2_steps * time_step
                else:
                    # Skip if it doesn't fit even 1 step
                    continue

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
    # 1. Octave filtering (existing logic)
    octave_filtered = []
    i = 0
    while i < len(notes):
        if i < len(notes) - 1 and abs(notes[i].start - notes[i+1].start) < 0.1:
            note_i = pretty_midi.note_number_to_name(notes[i].pitch)
            note_j = pretty_midi.note_number_to_name(notes[i+1].pitch)
            if note_i[:-1] == note_j[:-1]:
                note_to_keep = i if int(note_i[-1]) < int(note_j[-1]) else i + 1
                octave_filtered.append(notes[note_to_keep])
                i += 2
                continue
        octave_filtered.append(notes[i])
        i += 1

    # 2. Overlap filtering (Monophonic cleaning)
    # If notes overlap by more than 50% of the shorter note's duration, keep the longer one.
    monophonic_notes = []
    if not octave_filtered:
        return main_instrument

    current_note = octave_filtered[0]
    for next_note in octave_filtered[1:]:
        overlap = min(current_note.end, next_note.end) - max(current_note.start, next_note.start)
        if overlap > 0:
            shorter_duration = min(current_note.end - current_note.start, next_note.end - next_note.start)
            if overlap / shorter_duration > 0.5:
                # Significant overlap, keep the longer one
                if (current_note.end - current_note.start) < (next_note.end - next_note.start):
                    current_note = next_note
                continue
        
        monophonic_notes.append(current_note)
        current_note = next_note
    
    monophonic_notes.append(current_note)

    filtered_instrument = pretty_midi.Instrument(
        program=main_instrument.program,
        is_drum=main_instrument.is_drum,
        name=main_instrument.name
    )
    filtered_instrument.notes = monophonic_notes
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
    stream.append(m21.tempo.MetronomeMark(number=tempo))

    for note in filtered_instrument.notes:
        n = m21.note.Note(note.pitch)
        # Convert seconds to quarter lengths (beats)
        n.offset = note.start * (tempo / 60)
        n.quarterLength = (note.end - note.start) * (tempo / 60)
        stream.insert(n)

    # 3. QUANTIZE STREAM TO A 16th-note GRID
    quantized_stream = quantize(stream)
    
    # 4. TRANPOSE STREAM TO C/Am
    key, transposed_stream = tranpose(quantized_stream)

    encoded_song = encode_song(transposed_stream)

    return {
        "encoded_song": encoded_song,
        "tempo": tempo,
        "key": key
    }

def save_melody(melody, step_duration=0.25, file_format="midi", file_name="generated.mid", tempo=120):
    stream = m21.stream.Stream()
    stream.append(m21.tempo.MetronomeMark(number=tempo))
    
    if not melody:
        return

    i = 0
    while i < len(melody):
        symbol = melody[i]
        if symbol == "_":
            i += 1
            continue
            
        length = 1
        j = i + 1
        while j < len(melody) and melody[j] == "_":
            length += 1
            j += 1
            
        duration = length * step_duration
        if symbol == "r":
            m21_event = m21.note.Rest(quarterLength=duration)
        else:
            m21_event = m21.note.Note(int(symbol), quarterLength=duration)
        
        stream.append(m21_event)
        i = j
    
    stream.write(file_format, file_name)

if __name__ == "__main__":
    results = process_input("test.mp3")
    melody = results["encoded_song"].split()
    tempo = results["tempo"]
    print(f"Encoded melody: {melody}")
    print(f"Estimated tempo: {tempo}")
    save_melody(melody, tempo=tempo)

