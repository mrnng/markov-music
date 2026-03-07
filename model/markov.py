import pickle
import random
from pathlib import Path
# to save the model in a file and keep the tuples as tuples 
# since if we use json, we would have to convert them to string
# to save and back for it to work
# pickle saves them as binary

class MarkovModel:
    def __init__(self, order=1):
        self.model = {}
        self.order = order

    def fit(self, data):
        for i in range(len(data) - self.order):
            state = tuple(data[i:i + self.order])
            next_state = data[i + self.order]
            if state not in self.model:
                self.model[state] = {} 
            if next_state not in self.model[state]:
                self.model[state][next_state] = 0
            self.model[state][next_state] += 1

        for state in self.model:
            total = sum(self.model[state].values())
            for next_state in self.model[state]:
                self.model[state][next_state] /= total

    def generate(self, state):
        state = tuple(state)

        # try orders from "order" to 1, in case a state is not seen yet
        for k in range(self.order, 0, -1):
            sub_state = state[-k:]

            if sub_state in self.model:
                next_states = list(self.model[sub_state].keys())
                probs = list(self.model[sub_state].values())

                return random.choices(next_states, weights=probs)[0]

        # random choice if the above doesn't work
        if len(self.model) > 0:
            random_state = random.choice(list(self.model.keys()))
            next_states = list(self.model[random_state].keys())
            probs = list(self.model[random_state].values())
            return random.choices(next_states, weights=probs)[0]

        return None

    def generate_sequence(self, start_state, length):
        state = tuple(start_state)
        result = list(state)

        for _ in range(length):
            next_value = self.generate(state)
            if next_value is None:
                break
            result.append(next_value)
            state = tuple(result[-self.order:])

        return result

    def generate_from_data(self, data, length):
        if len(data) < self.order:
            raise ValueError("Data shorter than order")

        start_state = tuple(data[-self.order:])
        return self.generate_sequence(start_state, length)

    def save_model(self, file_name):
        file_path = Path(__file__).parent / file_name
        with open(file_path, "wb") as f:
            pickle.dump(self.model, f)

    def load_model(self, file_path):
        with open(file_path, "rb") as f:
            self.model = pickle.load(f)

