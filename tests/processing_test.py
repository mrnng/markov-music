from pathlib import Path
from processing.preprocessing import get_midi_data, midi_to_model_format
from processing.postprocessing import model_format_to_midi
from model.markov import MarkovModel

AUDIO_INPUT_FILEPATH = Path(__file__).parent / "piano-recording.m4a"
AUDIO_OUTPUT_FILEPATH = Path(__file__).parent / "generated-piano-recording.mid"

model = MarkovModel()
model.load_model("model/trained_model.pkl")

def test_pipeline(audio_filepath):
    midi_data = get_midi_data(audio_filepath)
    model_format = midi_to_model_format(midi_data)

    notes_sequence = model_format["notes"]
    # make sure they are tuples
    notes_sequence = [tuple(note) for note in notes_sequence]

    generated = model.generate_from_data(notes_sequence, 10)

    generated_model_format = {
        "tempo": model_format["tempo"],
        "tonic_midi": model_format["tonic_midi"],
        "notes": generated
    }
    return model_format_to_midi(generated_model_format)

output_midi = test_pipeline(AUDIO_INPUT_FILEPATH)
output_midi.write(AUDIO_OUTPUT_FILEPATH)
