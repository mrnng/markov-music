import json
import numpy as np
import music21 as m21
import tensorflow.keras as keras
from model.data_processing import SEQUENCE_LENGTH, MAPPING_PATH
from model.training import SAVE_MODEL_PATH
from model.training import OUTPUT_UNITS, NUM_UNITS, LOSS, LEARNING_RATE
from model.training import build_model

class MelodyGenerator:
    def __init__(self, model_path=SAVE_MODEL_PATH):
        self.model_path = model_path
        self.model = build_model(
            output_units=OUTPUT_UNITS,
            num_units=NUM_UNITS,
            loss=LOSS,
            learning_rate=LEARNING_RATE
        )

        self.model.load_weights(model_path)
        
        with open(MAPPING_PATH, "r") as f:
            self._mapping = json.load(f)

        self._start_symbols = ["/"] * SEQUENCE_LENGTH

    def generate_melody(self, seed, num_steps, max_sequence_length, temperature):
        seed = seed.split()
        melody = seed
        seed = self._start_symbols + seed
        seed = [self._mapping[symbol] for symbol in seed]

        for _ in range(num_steps):
            seed = seed[-max_sequence_length:]
            seed_input = np.array(seed)[np.newaxis, :]
            probabilities = self.model.predict(seed_input, verbose=0)[0]
            output_int = self._sample_with_temperature(probabilities, temperature)
            seed.append(output_int)
            output_symbol = [k for k, v in self._mapping.items() if v == output_int][0]
            if output_symbol == "/":
                break
            melody.append(output_symbol)

        return melody

    def _sample_with_temperature(self, probabilities, temperature):
        predictions = np.log(probabilities) / temperature
        probabilities = np.exp(predictions) / np.sum(np.exp(predictions))
        choices = range(len(probabilities))
        index = np.random.choice(choices, p=probabilities)
        return index

    def save_melody(self, melody, step_duration=0.25, file_format="midi", file_name="generated.mid"):
        stream = m21.stream.Stream()
        start_symbol = None
        step_counter = 1
        for idx, symbol in enumerate(melody):
            if start_symbol is None:
                start_symbol = symbol
                continue
            if symbol != "_" or idx + 1 == len(melody):
                if start_symbol is not None:
                    quarter_length_duration = step_duration * step_counter
                    if start_symbol == "r":
                        m21_event = m21.note.Rest(quarterLength=quarter_length_duration)
                    else:
                        m21_event = m21.note.Note(int(start_symbol), quarterLength=quarter_length_duration)
                    stream.append(m21_event)
                    step_counter = 1
                    start_symbol = symbol
            else:
                step_counter += 1
        
        stream.write(file_format, file_name)


if __name__ == "__main__":
    mg = MelodyGenerator()
    seed = "60 _ 60 _ 64 _ 67 _ _ _ _ _ 69 _"
    melody = mg.generate_melody(seed, 500, SEQUENCE_LENGTH, 0.3)
    mg.save_melody(melody)