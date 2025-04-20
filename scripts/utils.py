import numpy as np

def nonzero(M: np.ndarray) -> dict:
    values = {}
    h, w = M.shape
    for i in range(h):
        for j in range(w):
            if M[i, j] != 0:
                values[(i, j)] = M[i, j]
    return values