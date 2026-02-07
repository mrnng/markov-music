import os
from basic_pitch.inference import predict

def get_midi_data(audio_filepath):
    """
    Returns MIDI data from audio file as a PrettyMIDI object.
    """
    if not os.path.exists(audio_filepath):
        raise FileNotFoundError(f"File not found: {audio_filepath}")

    _, midi_data, _ = predict(audio_filepath)
    return midi_data