"""
Module containing miscellaneous utilities
"""

# Imports

import numpy as np

from timeit import default_timer as timer
from numba import jit


# Functions

def slow_get_first_index(array: np.ndarray, search_val: int | float | bool = True, method: str = "equal") -> int:
    
    array = np.ravel(array)
    
    if method == "equal":
    
        for index, value in enumerate(array):
            
            if value == search_val:
                
                return index
            
    elif method == "not":
        
        for index, value in enumerate(array):
            
            if value != search_val:
                
                return index
            
    elif method == "greater":
        
        for index, value in enumerate(array):
            
            if value > search_val:
                
                return index
    
    elif method == "greater or equal":
        
        for index, value in enumerate(array):
            
            if value >= search_val:
                
                return index
    
    elif method == "less":
        
        for index, value in enumerate(array):
            
            if value < search_val:
                
                return index
    
    elif method == "less or equal":
        
        for index, value in enumerate(array):
            
            if value <= search_val:
                
                return index

@jit(nopython = True)
def quick_get_first_index(array: np.ndarray, search_val: int | float | bool = True, method: str = "equal") -> int:
    
    array = np.ravel(array)
    
    if method == "equal":
    
        for index, value in enumerate(array):
            
            if value == search_val:
                
                return index
            
    elif method == "not":
        
        for index, value in enumerate(array):
            
            if value != search_val:
                
                return index
            
    elif method == "greater":
        
        for index, value in enumerate(array):
            
            if value > search_val:
                
                return index
    
    elif method == "greater or equal":
        
        for index, value in enumerate(array):
            
            if value >= search_val:
                
                return index
    
    elif method == "less":
        
        for index, value in enumerate(array):
            
            if value < search_val:
                
                return index
    
    elif method == "less or equal":
        
        for index, value in enumerate(array):
            
            if value <= search_val:
                
                return index

def compare_first_index(array: np.ndarray, search_val: int | float | bool = True, method: str = "equal") -> None:
    
    slow_start = timer()
    slow_get_first_index(array, search_val, method)
    slow_end = timer()
    quick_start = timer()
    quick_get_first_index(array, search_val, method)
    quick_end = timer()
    print(f"\nFinished operation in...\n\nSlow:  {(slow_end - slow_start): .3} s\nQuick: {(quick_end - quick_start): .3} s")


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()