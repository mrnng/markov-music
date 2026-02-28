from markov import load_model , generate
#just as a demo i loaded the model here 

model = load_model("./music-model.pkl")

state = (61,)
generate(model,state)

