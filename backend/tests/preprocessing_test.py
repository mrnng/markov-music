from pathlib import Path
from processing.preprocessing import get_midi_data
from processing.preprocessing import midi_to_model_format, model_format_to_midi
from pretty_midi import note_number_to_name
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH

AUDIO_FILEPATH = Path(__file__).parent / "piano-recording.m4a"

midi_data = get_midi_data(AUDIO_FILEPATH)

for instrument in midi_data.instruments:
    print(f"Program: {instrument.program}")
    for note in instrument.notes:
        print(f"Note: {note_number_to_name(note.pitch)}, start: {note.start:.2f}s, end: {note.end:.2f}s, velocity: {note.velocity}")

# predict_and_save(
#     [Path(__file__).parent / "piano-recording.m4a"],
#     Path(__file__).parent,
#     True, False, False, False,
#     ICASSP_2022_MODEL_PATH
# )

model = midi_to_model_format(midi_data)
print(model)
midi_from_model = model_format_to_midi(model)
print(midi_from_model.instruments)
midi_from_model.write(Path(__file__).parent / "piano-recording.mid")