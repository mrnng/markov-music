# modeling it up 


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

    print(result)
    return result


data = [1,1,3,2,4,7,6,4,1,2,3,4,4,4,5,6,8,9,1,2,2,1,0,3,4]

model = train(data,1)
state = (2,)
generate(model,state)