import numpy as np 


np.random.seed(190204)
X = np.random.randn(3, 3)
W = np.random.randn(3, 2)

def sigmoid(x : np.ndarray) -> np.ndarray : 
    return 1/(1+np.exp(-x))

def deriv(f , a , delta=0.001):
    return (f(a+delta)-f(a-delta))/(2*delta)

def forward_pass(X : np.ndarray , y : np.ndarray , weights : Dict[str , np.ndarray]) -> Tuple[Dict[str,np.ndarray] , float]:

    M1 = np.dot(X , weights['W1'])
    N1 = M1 + weights["B1"]
    O1 = sigmoid(N1)

    M2 = np.dot(O1 , weights["W2"])

    P = M2 + weights["B2"]

    # mean squared error loss 
    loss = np.mean(np.power(y-P, 2))

    forward_info: Dict[str, ndarray] = {}
    forward_info['X'] = X
    forward_info['M1'] = M1
    forward_info['N1'] = N1
    forward_info['O1'] = O1
    forward_info['M2'] = M2
    forward_info['P'] = P
    forward_info['y'] = y
    
    return forward_info, loss


#backward propagation
def back_prop(forward_info : Dict[str,np.ndarray]):

    dLdP = -2 * (forward_info["Y"] - forward_info["P"])

    dPdM2 = np.ones_like(forward_info["M2"])
    dPdB2 = np.ones_like(forward_info["B2"])


    dM2dW2 = np.transpose(forward_info["O1"] , (1,0))
    dM2dO1 = np.transpose(forward_info["W2"] , (1,0))

    dLdW2 = np.dot(dM2dW2 , dLdP)
    dLdO1 = np.dot(dM2dO1 , dLdP)

    dO1dN1 = sigmoid(forward_info["N1"]) * (1 - sigmoid(forward_info["N1"]))
    
    dN1dM1 = np.ones_like(forward_info["M1"])
    dN1dB1 = p.ones_like(forward_info["B1"])

    dM1dW1 = np.transpose(forward_info["X"] , (1,0))

    dO1dW1 = np.dot(dM1dW1 , dO1dN1)

    dLdW1 = np.dot(dO1dW1 , dLdW2)





