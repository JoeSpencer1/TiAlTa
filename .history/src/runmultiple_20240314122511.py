import multiprocessing
from multiprocessing import Pool
import numpy as np
import nn
import os

def run_main(arg):
    nn.main(arg)


if __name__ == '__main__':

    arguments = np.array([
        "validation_three('Er', 'TI33_25', 'TI33_25', 10, '3D_quad', 10, '2D_70', 10, typ='hi')",
        "validation_three('Er', 'TI33_25', 'TI33_25', 10, '3D_quad', 10, '2D_70', 10, typ='lo')",
        "validation_three('sigma_y', 'TI33_25', 'TI33_25', 10, '3D_quad', 10, '2D_70', 10, typ='hi')",
        "validation_three('sigma_y', 'TI33_25', 'TI33_25', 10, '3D_quad', 10, '2D_70', 10, typ='lo')",
        "validation_two('Er', 'TI33_25', 'TI33_25', 10, '3D_quad', 10)",
        "validation_two('sigma_y', 'TI33_25', 'TI33_25', 10, '3D_quad', 10)",
        "validation_one('Er', 'TI33_25', 'TI33_25', 10)",
        "validation_one('sigma_y', 'TI33_25', 'TI33_25', 10)"
        ])
    
    processes = []
    num_processes = len(arguments)
    for i in range(num_processes):        
        process = multiprocessing.Process(target=run_main, args=(arguments[i],))
        processes.append(process)

    for process in processes:
        process.start()
    for process in processes:
        process.join()
    with open('output.txt', 'a') as f:
        f.write('\n')