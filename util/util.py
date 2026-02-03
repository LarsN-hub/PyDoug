"""
Module containing miscellaneous utilities
"""


# Imports

import numpy as np

from numba import jit


# Globals

axes_dict_3d: dict[str, int] = {"X": 2, "Y": 1, "Z": 0}
axes_dict_2d: dict[str, int] = {"X": 1, "Y": 0}


# Functions


def convert_ax_str_to_int(im_layer: np.ndarray, rgb: bool, axis: str) -> int:
    
    if im_layer.data.ndim == 3 and not rgb:
        
        return axes_dict_3d[axis]
        
    elif im_layer.data.ndim == 4:
        
        return axes_dict_3d[axis]
        
    else:
        
        return axes_dict_2d[axis]
    
def reformat_bounds(bounds: int | list[int] = None, ax_len: int = 0, bounds_as_slices: bool = False) -> list[int]:
    
    if bounds == None:
        
        new_bounds = None
        
    else:
        
        new_bounds: int | list[int] = bounds.copy()
    
    if not bounds_as_slices:
        
        if not new_bounds:
            
            new_bounds = [0, ax_len]
            
        elif isinstance(new_bounds, int):
            
            new_bounds = [new_bounds, (ax_len - new_bounds)]
            
        elif len(new_bounds) == 1:
            
            new_bounds = [new_bounds[0], (ax_len - new_bounds[0])]
            
        else:
            
            new_bounds = [new_bounds[0], (ax_len - new_bounds[1])]
            
    else:
        
        if not new_bounds:
            
            new_bounds = [0, ax_len]
            
        elif isinstance(new_bounds, int):
            
            new_bounds = [new_bounds, ax_len]
            
        elif len(new_bounds) == 1:
            
            new_bounds = [new_bounds[0], ax_len]
        
    return new_bounds

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