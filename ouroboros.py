import math

def ouroboros(array, with_indice=False):
    """Compute the Ouroboros index of a list of frequencies.

    Return values:
    - Ouroboros index: a real number between 0 (min. uniformity) and 1 (max. uniformity)
    - (Ouroboros indice): a natural number between 0 and len(array)/2

    Keyword arguments:
    array -- array of numbers (count values or proportions)
    with_indice -- also return the Ouroboros indice (default: False)
    """
    A = sorted(list(array))
    N = len(A)
    S = sum(A)
    acc = 0
    idc = 0
    
    if N <= 1:
        return (1, 1) if with_indice else 1
    
    while acc < (S/2):
        acc += A.pop()
        idc += 1

    imax = math.ceil(N/2)
    pmin = 1/N * imax
    p = acc/S
    d = (p - pmin) / (1 - pmin) 
    idx = (idc-d) / imax
    
    if with_indice:
        return idx, idc
    
    return idx
