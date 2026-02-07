from pathlib import Path
from processing.audio_to_midi import get_midi_data
from pretty_midi import note_number_to_name

AUDIO_FILEPATH = Path(__file__).parent / "c-major-scale.mp3"

midi_data = get_midi_data(AUDIO_FILEPATH)

for instrument in midi_data.instruments:
    print(f"Program: {instrument.program}")
    for note in instrument.notes:
        print(f"Note: {note_number_to_name(note.pitch)}, start: {note.start:.2f}s, end: {note.end:.2f}s, velocity: {note.velocity}")
