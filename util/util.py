"""
Module containing miscellaneous utilities
"""

# Imports

import numpy as np

from numba import jit


# Functions

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

@jit(nopython = True)
def quick_get_indices(array: np.ndarray, sorted_vals: np.ndarray, method: str = "greater or equal") -> np.ndarray:
    
    array = np.ravel(array)
    sorted_vals = np.ravel(sorted_vals)
    output_array: np.ndarray = np.empty(len(sorted_vals))
    output_index: int = 0
    
    if method == "greater or equal":
    
        for index, value in enumerate(array):
        
            if value >= sorted_vals[output_index]:
                
                output_array[output_index] = index
                output_index += 1
                
    return output_array


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()