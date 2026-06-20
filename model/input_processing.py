import os
import copy
import math
import tempfile
import music21
import pretty_midi
from basic_pitch.inference import predict

ALLOWED_DURATIONS = [2**i for i in range(-4, 3)]

def estimate_key(midi_data):
    
    temp_midi = tempfile.NamedTemporaryFile(delete=False, suffix=".mid")
    temp_midi.close()  

    try:
        midi_data.write(temp_midi.name)
        score = music21.converter.parse(temp_midi.name)
        key = score.analyze('key')
        return f"{key.tonic.name}-{key.mode}"
        
    finally:
        if os.path.exists(temp_midi.name):
            os.remove(temp_midi.name)

def get_midi_data(audio_path):
    _, midi_data, _ = predict(audio_path)
    return midi_data

def filter_notes(notes):
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
    return filtered_notes

def quantize_notes(notes, tempo, subdivision=16):
    quantized = copy.deepcopy(notes)

    seconds_per_beat = 60.0 / tempo

    grid = seconds_per_beat * (4 / subdivision)

    for note in quantized:
        q_start = round(note.start / grid) * grid
        q_end = round(note.end / grid) * grid
        if q_end <= q_start:
            q_end = q_start + grid

        note.start = q_start
        note.end = q_end

    return quantized

def force_no_overlap(notes):
    if not notes:
        return notes

    # assume notes already sorted by start time
    cleaned = []

    for i in range(len(notes)):
        note = copy.deepcopy(notes[i])

        if i < len(notes) - 1:
            next_note = notes[i + 1]

            # hard clamp: current note must end exactly where next starts
            note.end = min(note.end, next_note.start)
            note.end = max(note.end, note.start)  # safety

        cleaned.append(note)

    return cleaned

def snap_duration(duration):
    return min(ALLOWED_DURATIONS, key=lambda x: abs(x - duration))

def enforce_power_of_two_durations(notes, tempo):
    seconds_per_beat = 60.0 / tempo
    cleaned = []

    for note in notes:
        n = copy.deepcopy(note)

        duration_beats = (n.end - n.start) / seconds_per_beat
        snapped_beats = snap_duration(duration_beats)

        n.end = n.start + snapped_beats * seconds_per_beat
        cleaned.append(n)

    return cleaned

def get_melody(midi_data):
    melody = {}

    tempo = midi_data.estimate_tempo()
    melody["tempo"] = tempo

    main_instrument = max(midi_data.instruments, key=lambda i: len(i.notes))
    notes = sorted(main_instrument.notes, key=lambda n: n.start)
    notes = filter_notes(notes)
    notes = quantize_notes(notes, tempo=tempo, subdivision=16)
    notes = force_no_overlap(notes)
    notes = enforce_power_of_two_durations(notes, tempo)
    melody["notes"] = notes

    melody_midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0)
    instrument.notes = notes
    melody_midi.instruments.append(instrument)
    key = estimate_key(melody_midi)
    melody["key"] = key

    return melody

def notes_to_melody_sequence(notes, tempo):
    seconds_per_beat = 60.0 / tempo

    sequence = []
    for note in notes:
        duration_seconds = note.end - note.start
        duration_beats = duration_seconds / seconds_per_beat

        sequence.append((note.pitch, round(duration_beats, 4)))

    return sequence

def melody_to_model_format(sequence, time_step=0.25):
    encoded_song = []

    for symbol, duration in sequence:
        steps = int(round(duration / time_step))
        for step in range(steps):
            if step == 0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")

    return " ".join(str(s) for s in encoded_song)

def cap_trailing_rest(sequence, cap=7):
    if not sequence:
        return sequence

    tokens = sequence.split()
    count = 0
    i = len(tokens) - 1
    while i >= 0 and tokens[i] == "_":
        count += 1
        i -= 1
    if count > cap:
        tokens = tokens[:len(tokens) - (count - cap)]
    return " ".join(tokens)

def melody_to_midi(melody, output_path="melody.mid"):
    midi = pretty_midi.PrettyMIDI()

    instrument = pretty_midi.Instrument(program=0, name="Melody")
    instrument.notes.extend(melody["notes"])

    midi.instruments.append(instrument)
    midi.write(output_path)

def process_input(audio_path):
    midi_data = get_midi_data(audio_path)
    melody = get_melody(midi_data)
    sequence = notes_to_melody_sequence(melody["notes"], melody["tempo"])
    sequence = melody_to_model_format(sequence)
    sequence = cap_trailing_rest(sequence)
    print(sequence)
    return sequence

if __name__ == "__main__":
    INPUT_PATH = "test.mp3"
    midi_data = get_midi_data(INPUT_PATH)
    melody = get_melody(midi_data)
    sequence = notes_to_melody_sequence(melody["notes"], melody["tempo"])
    print(melody_to_model_format(sequence))
    melody_to_midi(melody, "melody.mid")
