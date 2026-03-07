from model.markov import MarkovModel

markov_model = MarkovModel(order=2)
markov_model.load_model("model/test_model.pkl")

test_data = [60, 62, 64, 65, 67, 65, 64, 62]
generated_sequence = markov_model.generate_from_data(test_data, length=5)
print(generated_sequence)