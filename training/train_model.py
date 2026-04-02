import os
import pretty_midi
from pathlib import Path
from model.markov import MarkovModel
from processing.preprocessing import get_midi_data, midi_to_model_format

MIDI_FOLDER = "Records_to_MIDI"
ORDER = 2
OUTPUT_FILE = "trained_model.pkl"

all_sequences = []

for file_name in os.listdir(MIDI_FOLDER):
    if not file_name.lower().endswith(".mid"):
        continue

    file_path = os.path.join(MIDI_FOLDER, file_name)
    try:
        midi_data = pretty_midi.PrettyMIDI(file_path)
        model_format = midi_to_model_format(midi_data)
        notes = model_format["notes"]

        if len(notes) > 0:
            all_sequences.append(notes)
    except Exception as e:
        print(f"Failed to process {file_name}: {e}")

flattened = [note for seq in all_sequences for note in seq]

model = MarkovModel(order=ORDER)
model.fit(flattened)

model.save_model(OUTPUT_FILE)
print(f"Model saved to {OUTPUT_FILE}")