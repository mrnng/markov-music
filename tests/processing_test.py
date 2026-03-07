from pathlib import Path
from processing.preprocessing import get_midi_data, midi_to_model_format
from processing.postprocessing import model_format_to_midi

AUDIO_INPUT_FILEPATH = Path(__file__).parent / "piano-recording.m4a"
AUDIO_OUTPUT_FILEPATH = Path(__file__).parent / "piano-recording.mid"

def test_pipeline(audio_filepath):
    midi_data = get_midi_data(audio_filepath)
    model_format = midi_to_model_format(midi_data)
    output_midi = model_format_to_midi(model_format)
    return output_midi

output_midi = test_pipeline(AUDIO_INPUT_FILEPATH)
output_midi.write(AUDIO_OUTPUT_FILEPATH)
