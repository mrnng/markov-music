from model.markov import MarkovModel

test_data = [60, 62, 64, 65, 67, 65, 64, 62]
markov_model = MarkovModel(order=2)
markov_model.fit(test_data)

markov_model.save_model("test_model.pkl")