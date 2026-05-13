"""
Module containing miscellaneous utilities
"""


# Imports

import matplotlib as mpl
import numpy as np
import napari
import math

from matplotlib import colormaps, colorbar as cbar, colors, pyplot as plt

from PyDoug.proc import trans, cropclip as cc


# Globals

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"
label_fontsize = 15
tick_fontsize = 13


# Functions

def correct_mask(
        im_array: np.ndarray,
        mask_array: np.ndarray = None,
        axis: int = 0) -> np.ndarray:
    
    if np.any(mask_array):
        
        bool_array = np.bool(mask_array)
        
        if bool_array.ndim < im_array.ndim:
            
            bool_array = get_along_axis_array(
                cc.project_mask(
                    bool_array,
                    im_array.shape[0]),
                axis)
            
    else:
        
        bool_array: None = None
        
    return bool_array

def get_colormap(
        im_array: np.ndarray = None, *,
        lab_limits: tuple = None,
        cmap: str = "inferno",
        return_cbar: bool = True,
        cbar_scale: float = 1,
        cbar_units: str = "pix",
        cbar_label: str = "Units") -> napari.utils.DirectLabelColormap:
    
    if not lab_limits:
        
        lab_limits: tuple = (np.unique(im_array)[0], np.unique(im_array)[-1])
        
    else:
          
        if lab_limits[0] == 0:
            
            lab_limits: tuple = (0, int(lab_limits[1] / cbar_scale))
        
        else:
            
            lab_limits: tuple = (int(lab_limits[0] / cbar_scale), int(lab_limits[1] / cbar_scale))
        
    color_dict: dict = {0: np.array([0, 0, 0, 0])}
    nonzero_label_count: int = np.count_nonzero(
        np.arange(min(lab_limits),
                  max(lab_limits) + 1))
        
    if min(lab_limits) == 0:
            
        lab_limits = (1, max(lab_limits))
        
    color_grad_array: np.ndarray = colormaps[cmap](np.linspace(0, 1, nonzero_label_count))
    color_dict[None] = color_grad_array[-1, :]
            
    for label_index, actual_label in enumerate(range(min(lab_limits), (max(lab_limits) + 1))):
                
        color_dict[actual_label] = color_grad_array[label_index, :]
            
    for actual_label in range(1, min(lab_limits)):
                
        color_dict[actual_label] = color_grad_array[0, :]
        
    cmap_return: napari.utils.DirectLabelColormap = napari.utils.DirectLabelColormap(
        color_dict = color_dict)
    cmap_return.name: str = cmap
        
    if return_cbar:
        
        if cbar_units == "um":
            
            cbar_units = "\u00b5m"
        
        if cbar_units:
            
            c_label: str = f"{cbar_label} ({cbar_units})"
            
        else:
            
            c_label: str = cbar_label
            
        fig, ax = plt.subplots(layout = "constrained")
        fig_cbar: cbar.Colorbar = fig.colorbar(
            mpl.cm.ScalarMappable(
                norm = colors.Normalize(
                    (min(lab_limits) * cbar_scale),
                    (max(lab_limits) * cbar_scale)),
                cmap = cmap),
            ax = ax)
        fig_cbar.set_label(
            c_label,
            rotation = 270,
            va = "bottom",
            fontsize = label_fontsize)
        fig_cbar.ax.tick_params(labelsize = tick_fontsize)
        
        return cmap_return, fig
    
    else:
        
        return cmap_return

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

def get_along_axis_array(
        im_array: np.ndarray,
        axis: int | None = None) -> np.ndarray:
    
    if axis == 1:
        
        return trans.reslice(im_array, "top")
        
    elif axis == 2:
        
        return trans.reslice(im_array, "left")
        
    else:
        
        return im_array
    
def undo_axial_array(
        im_array: np.ndarray,
        axis: int | None = None) -> np.ndarray:
    
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
        
        return {"Min": np.iinfo(im_array.dtype).min,
                "Max": np.iinfo(im_array.dtype).max}
    
    elif np.issubdtype(im_array.dtype, np.floating):
        
        return {"Min": np.finfo(im_array.dtype).min,
                "Max": np.finfo(im_array.dtype).max}
    
    elif im_array.dtype == np.bool:
        
        return {"Min": 0, "Max": 1}
    
def convert_color_to_intensity(
        im_array: np.ndarray,
        color: str,
        dtype_dict: dict[str, float, int] = None) -> float | int:
    
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

def get_ax_str_dim(im_array: np.ndarray, ax_str: str,) -> int:
    
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

def convert_ax_str_to_int(
        im_array: np.ndarray,
        rgb: bool,
        axis: str,
        axial_operation_axis: str = None) -> int:
    
    axes_dict_3d: dict[str, int] = {"x": 2, "y": 1, "z": 0}
    axes_dict_2d: dict[str, int] = {"x": 1, "y": 0, "z": -1}
    
    if axial_operation_axis:
        
        eval_axis: str = axial_operation_axis
        
    else:
        
        eval_axis: str = axis
    
    if im_array.ndim == 3 and not rgb:
        
        ax_int: int = axes_dict_3d[eval_axis.lower()]
        
    elif im_array.ndim == 4:
        
        ax_int: int = axes_dict_3d[eval_axis.lower()]
        
    else:
        
        ax_int: int = axes_dict_2d[eval_axis.lower()]
        
    if not axial_operation_axis:
        
        return ax_int
    
    else:
        
        if is_3d_rgb(im_array)["3D"]:
            
            if ax_int == 0:
                
                if axis.lower() == "x":
                    
                    return 1
                
                elif axis.lower() == "y":
                    
                    return 0
                
                elif axis.lower() == "z":
                    
                    return None
            
            elif ax_int == 1:
                
                if axis.lower() == "x":
                    
                    return 1
                
                elif axis.lower() == "y":
                    
                    return None
                
                elif axis.lower() == "z":
                    
                    return 0
            
            elif ax_int == 2:
                
                if axis.lower() == "x":
                    
                    return None
                
                elif axis.lower() == "y":
                    
                    return 0
                
                elif axis.lower() == "z":
                    
                    return 1
            
        
        else:
            
            return axes_dict_2d[axis.lower()]
    
def reformat_bounds(
        bounds: int | list[int] = None,
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
                
                new_bounds = [new_bounds,
                              (ax_len - new_bounds)]
                
            elif len(new_bounds) == 1:
                
                new_bounds = [new_bounds[0],
                              (ax_len - new_bounds[0])]
                
            else:
                
                new_bounds = [new_bounds[0],
                              (ax_len - new_bounds[1])]
                
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
                    
                    new_bounds = [int(pad_amount),
                                  int(pad_amount)]
                    
                else:
                    
                    new_bounds = [int(math.ceil(pad_amount)),
                                  int(math.floor(pad_amount))]
                
            elif len(new_bounds) == 1:
                
                pad_amount: float = (new_bounds[0] - ax_len) / 2
                
                if pad_amount % 1 == 0:
                    
                    new_bounds = [int(pad_amount),
                                  int(pad_amount)]
                    
                else:
                    
                    new_bounds = [int(math.ceil(pad_amount)),
                                  int(math.floor(pad_amount))]
                
            else:
                
                pad_amount: float = (new_bounds[1] - ax_len) / 2
                
                if pad_amount % 1 == 0:
                    
                    new_bounds = [int(pad_amount),
                                  int(pad_amount)]
                    
                else:
                    
                    new_bounds = [int(math.ceil(pad_amount)),
                                  int(math.floor(pad_amount))]
        
    return new_bounds


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()