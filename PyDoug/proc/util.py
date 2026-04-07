"""
Module containing miscellaneous utilities
"""


# Imports

import numpy as np
import napari
import math

from numba import jit

from PyDoug.proc import trans


# Functions

def get_layer_type(layer: napari.layers.Layer) -> str:
    
    if isinstance(layer, napari.layers.Image):
        
        return "image"
    
    elif isinstance(layer, napari.layers.Shapes):
        
        return "shapes"
    
    elif isinstance(layer, napari.layers.Labels):
        
        return "labels"
    
    elif isinstance(layer, napari.layers.Points):
        
        return "points"
    
    elif isinstance(layer, napari.layers.Surface):
        
        return "surface"
    
    elif isinstance(layer, napari.layers.Tracks):
        
        return "tracks"
    
    elif isinstance(layer, napari.layers.Vectors):
        
        return "vectors"
    
    else:
        
        return None

def get_in_plane_dims(im_array: np.ndarray) -> tuple[int]:
    
    if im_array.ndim == 2:
        
        return (im_array.shape[0], im_array.shape[1])
    
    else:
        
        if is_3d_rgb(im_array)["3D"]:
            
            return (im_array.shape[1], im_array.shape[2])
        
        else:
        
            return (im_array.shape[0], im_array.shape[1])

def find_order_of_mag(value: float | int) -> float | int:
    
    return math.floor(math.log10(value))

def check_if_square(im_array: np.ndarray) -> bool:
    
    if im_array.ndim == 2:
        
        if im_array.shape[0] != im_array.shape[1]:
            
            return False
        
        else:
            
            return True
        
    elif im_array.ndim == 3:
        
        if im_array.shape[1] != im_array.shape[2]:
            
            return False
        
        else:
            
            return True
        
    else:
        
        return False

def get_along_axis_array(im_array: np.ndarray, axis: int) -> np.ndarray:
    
    if axis == 1:
        
        return trans.reslice(im_array, "top")
        
    elif axis == 2:
        
        return trans.reslice(im_array, "left")
        
    else:
        
        return im_array
    
def undo_axial_array(im_array: np.ndarray, axis: int) -> np.ndarray:
    
    if axis == 1:
        
        return trans.reslice(im_array, "bottom")
        
    elif axis == 2:
        
        return trans.reslice(im_array, "right")
        
    else:
        
        return im_array

def dict_list_to_list_list(dict_list: list[dict]) -> list[list]:
    
    list_list: list[list] = []
    
    for row in dict_list:
        
        cur_list: list = []
        
        for item in list(row.keys()):
            
            cur_list.append(item)
            cur_list.append(row[item])
            
        list_list.append(cur_list)
    
    return list_list

def list_list_to_dict_list(list_list: list[list]) -> list[dict]:
    
    dict_list: list[dict] = []
    
    for row in list_list:
        
        cur_dict: dict = {}
        
        for index in range(0, len(row), 2):
            
            cur_dict[row[index]] = row[index + 1]
            
        dict_list.append(cur_dict)
    
    return dict_list

def get_dtype_info(im_array: np.ndarray) -> dict[str, float, int]:
    
    if np.issubdtype(im_array.dtype, np.integer):
        
        return {"Min": np.iinfo(im_array.dtype).min, "Max": np.iinfo(im_array.dtype).max}
    
    elif np.issubdtype(im_array.dtype, np.floating):
        
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
        
        if np.issubdtype(im_array.dtype, np.integer):
            
            return int(round((dtype_dict["Max"] - dtype_dict["Min"]) / 2))
        
        elif np.issubdtype(im_array.dtype, np.floating):
            
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

def get_ax_str_dim(im_array: np.ndarray, ax_str: str) -> int:
    
    if ax_str.lower() == "x":
        
        if is_3d_rgb(im_array)["3D"]:
            
            return im_array.shape[2]
        
        else:
            
            return im_array.shape[1]
        
    elif ax_str.lower() == "y":
        
        if is_3d_rgb(im_array)["3D"]:
            
            return im_array.shape[1]
        
        else:
            
            return im_array.shape[0]
        
    elif ax_str.lower() == "z":
        
        if is_3d_rgb(im_array)["3D"]:
            
            return im_array.shape[0]
        
        else:
            
            return None

def convert_ax_str_to_int(im_array: np.ndarray, rgb: bool, axis: str) -> int:
    
    axes_dict_3d: dict[str, int] = {"X": 2, "Y": 1, "Z": 0}
    axes_dict_2d: dict[str, int] = {"X": 1, "Y": 0, "Z": -1}
    
    if im_array.ndim == 3 and not rgb:
        
        return axes_dict_3d[axis]
        
    elif im_array.ndim == 4:
        
        return axes_dict_3d[axis]
        
    else:
        
        return axes_dict_2d[axis]
    
def reformat_bounds(bounds: int | list[int] = None,
                    ax_len: int = 0,
                    bounds_as_slices: bool = False,
                    method: str = "trim") -> list[int]:
    
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
                
            else:
                
                if new_bounds[1] == 0:
                    
                    new_bounds[1] = ax_len
                
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