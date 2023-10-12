import matplotlib.pyplot as plt 
import torch

probabilities = [-float("inf"), -1.7811e+01, -1.7745e+01, -1.7745e+01, -1.7728e+01, -1.7137e+01, -1.7132e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.7079e+01, -1.4917e+01, -1.2519e+01, -2.1338e-05, -1.5435e-02, -1.5465e-02, -1.8864e+00, -1.1601e+01, -1.2099e+01, -1.4079e+01, -1.4079e+01, -1.4449e+01, -1.4463e+01, -1.3445e+01, -1.3523e+01, -1.4818e+01, -1.7557e+01, -2.4865e+01, -2.7153e+01, -1.9285e+01, -1.9285e+01, -8.7901e+00, -1.2113e+01, -1.4900e+01, -1.5734e+01, -2.9827e+01, -2.9831e+01]
max_index = probabilities.index(max(probabilities))
max_probability = probabilities[max_index]

indices = list(range(len(probabilities)))
j = len(indices) - 2
while j >= 0 :
    if probabilities[indices[j]] == probabilities[indices[j+1]] :
        indices = indices[:j] + indices[j+1:]
    j -= 1


j = len(indices) - 2
while j > 0 :
    if probabilities[indices[j-1]] < probabilities[indices[j]] and probabilities[indices[j]] < probabilities[indices[j+1]] :
        indices = indices[:j] + indices[j+1:]
    if probabilities[indices[j-1]] > probabilities[indices[j]] and probabilities[indices[j]] > probabilities[indices[j+1]] :
        indices = indices[:j] + indices[j+1:]
    j -= 1

x = [i for i in range(len(probabilities))]
y1 = probabilities
y2 = [probabilities[i] for i in indices]
print(y2[1::2])
