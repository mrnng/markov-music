# modeling it up 
import pickle
#to save the model in a file and keep the tuple as tuples 
#since json we would have to convert them to string to save and back for it to work 
#pickle saves them as binary

def train(data,order):
    model={}

    for i in range(len(data)-order):
        state = tuple(data[i:i+order])
        next = data[i+order]

        if state not in model:
            model[state] = {} 

        if next not in model[state]:
            model[state][next] = 0

        model[state][next] += 1

    for state in model :
        total = 0 

        for next in model[state]:
            total += model[state][next]

        for next in model[state]:
            model[state][next] /= total
    print("success")
    return model

def generate(model,state):
    result = None 
    proba = 0 

    if state not in model:
        print("state not in model")
        return None


    for next in model[state]:
        if proba < model[state][next]:
            proba = model[state][next]
            result = next 
            print("result "+str(result)+" with proba of :"+str(proba))

    return result

def save_model(model,file):
    with open(file,"wb") as f:
        pickle.dump(model,f)

def load_model(file):
    with open(file,"rb") as f:
        return pickle.load(f)

data = [63, 61, 65, 60, 64, 62, 63, 60, 65, 61, 64, 62, 60, 63, 65, 61, 62, 64, 60, 63, 63, 61, 65, 60, 64, 62, 63, 60, 65, 61, 64, 62, 60, 63, 65, 61, 62, 64, 60, 63]

model = train(data,1)

save_model(model,"music-model.pkl")
