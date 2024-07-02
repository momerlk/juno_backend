import numpy as np 

Weights = np.array([0.22,0.1,0.01,0.48,0.1,0.05,0.01,0.01,0.01,0.01])
print(f"Sum of weights = {np.sum(Weights)}")
Ratings_omer = np.array([10,10,7,10,9,10,10,10,7,10])
Ratings_amr = np.array([4,10,7,10,9,6,9,10,7,10])
Ratings_abr = np.array([0,5,1,2,7,0,8,6,5,7])

score_omer = 0
score_amr = 0
score_abr = 0

for idx, R in enumerate(Ratings_omer) : 
    score_omer += Weights[idx]*Ratings_omer[idx]

for idx, R in enumerate(Ratings_amr) : 
    score_amr += Weights[idx]*Ratings_amr[idx]

for idx, R in enumerate(Ratings_abr) : 
    score_abr += Weights[idx]*Ratings_abr[idx] 

total_score = score_omer + score_amr + score_abr
omer_reserved = 0
amr_reserved = 0

def get_percentage(value,total):
    return (value/total)*(100-(omer_reserved+amr_reserved))

print(f"Equity for omer = {get_percentage(score_omer,total_score) + omer_reserved} , Equity for Amr = {get_percentage(score_amr,total_score) + amr_reserved}, Equity for Abr = {get_percentage(score_abr,total_score)}")