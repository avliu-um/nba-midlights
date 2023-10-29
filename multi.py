from multiprocessing import Pool
from itertools import starmap

def f(x,y):
    return x*y

if __name__ == '__main__':
    with Pool(5) as p:
        print(p.starmap(f, [(1,4), (2,5), (3,6)]))
