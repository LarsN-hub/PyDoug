"""
Module containing miscellaneous utilities
"""


# Imports

import numpy as np
import math

from numba import jit


# Globals

int_dtypes: list[np.dtype] = [np.uint8, np.uint16, np.uint32, np.uint64, np.int8, np.int16, np.int32, np.int64]
float_dtypes: list[np.dtype] = [np.float16, np.float32, np.float64]
axes_dict_3d: dict[str, int] = {"X": 2, "Y": 1, "Z": 0}
axes_dict_2d: dict[str, int] = {"X": 1, "Y": 0}


# Functions

def get_dtype_info(im_array: np.ndarray) -> dict[str, float, int]:
    
    if im_array.dtype in int_dtypes:
        
        return {"Min": np.iinfo(im_array.dtype).min, "Max": np.iinfo(im_array.dtype).max}
    
    elif im_array.dtype in float_dtypes:
        
        return {"Min": np.finfo(im_array.dtype).min, "Max": np.finfo(im_array.dtype).max}
    
    elif im_array.dtype == np.bool:
        
        return {"Min": 0, "Max": 1}
    
def convert_color_to_intensity(im_array: np.ndarray, color: str, dtype_dict: dict[str, float, int] = None) -> float | int:
    
    if not dtype_dict:
        
        dtype_dict = get_dtype_info(im_array)
    
    if color == "Black":
        
        return dtype_dict["Min"]
    
    elif color == "White":
        
        return dtype_dict["Max"]
    
    elif color == "Gray":
        
        if im_array.dtype in int_dtypes:
            
            return int(round((dtype_dict["Max"] - dtype_dict["Min"]) / 2))
        
        elif im_array.dtype in float_dtypes:
            
            return (dtype_dict["Max"] - dtype_dict["Min"]) / 2
        
        elif im_array.dtype == np.bool:
            
            return 1

def is_3d_rgb(im_array: np.ndarray) -> dict[str, bool]:
    
    if im_array.ndim == 3:
        
        if im_array.shape[2] == 3:
            
            is_rgb: bool = True
            is_3d: bool = False
            
        else:
            
            is_rgb: bool = False
            is_3d: bool = True
        
    elif im_array.ndim == 4:
        
        is_rgb: bool = True
        is_3d: bool = True
        
    elif im_array.ndim == 2:
    
        is_rgb: bool = False
        is_3d: bool = False
        
    return {"3D": is_3d, "RGB": is_rgb}

def convert_ax_str_to_int(im_layer: np.ndarray, rgb: bool, axis: str) -> int:
    
    if im_layer.data.ndim == 3 and not rgb:
        
        return axes_dict_3d[axis]
        
    elif im_layer.data.ndim == 4:
        
        return axes_dict_3d[axis]
        
    else:
        
        return axes_dict_2d[axis]
    
def reformat_bounds(bounds: int | list[int] = None, ax_len: int = 0, bounds_as_slices: bool = False, method: str = "trim") -> list[int]:
    
    if bounds == None:
        
        new_bounds = None
        
    else:
        
        new_bounds: int | list[int] = bounds.copy()
        
    if method == "trim":
    
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
                
    elif method == "pad":
        
        if not bounds_as_slices:
            
            if not new_bounds:
                
                new_bounds = [0, 0]
                
            elif isinstance(new_bounds, int):
                
                new_bounds = [new_bounds] * 2
                
            elif len(new_bounds) == 1:
                
                new_bounds = [new_bounds[0]] * 2
                
        else:
            
            if not new_bounds:
                
                new_bounds = [0, 0]
                
            elif isinstance(new_bounds, int):
                
                pad_amount: float = (new_bounds - ax_len) / 2
                
                if pad_amount % 1 == 0:
                    
                    new_bounds = [int(pad_amount), int(pad_amount)]
                    
                else:
                    
                    new_bounds = [int(math.ceil(pad_amount)), int(math.floor(pad_amount))]
                
            elif len(new_bounds) == 1:
                
                pad_amount: float = (new_bounds[0] - ax_len) / 2
                
                if pad_amount % 1 == 0:
                    
                    new_bounds = [int(pad_amount), int(pad_amount)]
                    
                else:
                    
                    new_bounds = [int(math.ceil(pad_amount)), int(math.floor(pad_amount))]
                
            else:
                
                pad_amount: float = (new_bounds[1] - ax_len) / 2
                
                if pad_amount % 1 == 0:
                    
                    new_bounds = [int(pad_amount), int(pad_amount)]
                    
                else:
                    
                    new_bounds = [int(math.ceil(pad_amount)), int(math.floor(pad_amount))]
        
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