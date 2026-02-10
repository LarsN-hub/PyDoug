"""
Module for cropping, clipping, and padding image dimensions
"""

# Imports

import sliceview as sv
import numpy as np
import napari
import math
import util

from skimage import draw


# Functions

def trim_pad_bounds(im_array: np.ndarray, x_bounds: int | list[int] = None, y_bounds: int | list[int] = None, z_bounds: int | list[int] = None, bounds_dict: dict[str, list[int]] = None, bounds_as_slices: bool = False, method: str = "trim") -> dict[int, list[int]]:
    
    is_3d_rgb_dict = util.is_3d_rgb(im_array)
        
    if bounds_dict:
        
        x_bounds = bounds_dict["X"]
        y_bounds = bounds_dict["Y"]
        z_bounds = bounds_dict["Z"]
            
    x_ax: int = util.convert_ax_str_to_int(im_array, is_3d_rgb_dict["RGB"], "X")
    y_ax: int = util.convert_ax_str_to_int(im_array, is_3d_rgb_dict["RGB"], "Y")
    x_bounds: list[int] = util.reformat_bounds(x_bounds, im_array.shape[x_ax], bounds_as_slices, method)
    y_bounds: list[int] = util.reformat_bounds(y_bounds, im_array.shape[y_ax], bounds_as_slices, method)
    bounds: dict[int, list] = {x_ax: x_bounds, y_ax: y_bounds}
    
    if is_3d_rgb_dict["3D"]:
        
        z_ax: int = util.convert_ax_str_to_int(im_array, is_3d_rgb_dict["RGB"], "Z")
        z_bounds: list[int] = util.reformat_bounds(z_bounds, im_array.shape[z_ax], bounds_as_slices, method)
        bounds[z_ax] = z_bounds
        
    return bounds

def trim(im_array: np.ndarray, x_bounds: int | list[int] = None, y_bounds: int | list[int] = None, z_bounds: int | list[int] = None, *, bounds_dict: dict[str, list[int]] = None, bounds_as_slices: bool = False, conserve_mem: bool = False) -> np.ndarray:
    
    bounds = trim_pad_bounds(im_array, x_bounds, y_bounds, z_bounds, bounds_dict, bounds_as_slices, "trim")
    is_3d_rgb_dict = util.is_3d_rgb(im_array)
    
    if conserve_mem:
        
        if not is_3d_rgb_dict["3D"]:
                
            return im_array[bounds[0][0]:bounds[0][1], bounds[1][0]:bounds[1][1]]
                
        else:
                
            return im_array[bounds[0][0]:bounds[0][1], bounds[1][0]:bounds[1][1], bounds[2][0]:bounds[2][1]]
    
    else:
        
        if not is_3d_rgb_dict["3D"]:
                
            trim_array: np.ndarray = im_array[bounds[0][0]:bounds[0][1], bounds[1][0]:bounds[1][1]]
                
        else:
                
            trim_array: np.ndarray = im_array[bounds[0][0]:bounds[0][1], bounds[1][0]:bounds[1][1], bounds[2][0]:bounds[2][1]]
        
        return trim_array
    
def pad_operation(im_array: np.ndarray, bounds: dict[int, list[int]], padded_color: float | int) -> np.ndarray:
    
    is_3d_rgb_dict = util.is_3d_rgb(im_array)
    
    if not is_3d_rgb_dict["3D"]:
            
        left_x_insert: np.ndarray = np.ones((im_array.shape[0], bounds[1][0])) * padded_color
        right_x_insert: np.ndarray = np.ones((im_array.shape[0], bounds[1][1])) * padded_color
        im_array = np.insert(im_array, 0, left_x_insert, axis = 1)
        im_array = np.append(im_array, right_x_insert, axis = 1)
        top_y_insert: np.ndarray = np.ones((bounds[0][0], im_array.shape[1])) * padded_color
        bot_y_insert: np.ndarray = np.ones((bounds[0][1], im_array.shape[1])) * padded_color
        im_array = np.insert(im_array, 0, top_y_insert, axis = 0)
        im_array = np.append(im_array, bot_y_insert, axis = 0)
            
    else:
        
        left_x_insert: np.ndarray = np.ones((im_array.shape[0], im_array.shape[1], bounds[2][0])) * padded_color
        right_x_insert: np.ndarray = np.ones((im_array.shape[0], im_array.shape[1], bounds[2][1])) * padded_color
        im_array = np.insert(im_array, [0], left_x_insert, axis = 2)
        im_array = np.append(im_array, right_x_insert, axis = 2)
        top_y_insert: np.ndarray = np.ones((im_array.shape[0], bounds[1][0], im_array.shape[2])) * padded_color
        bot_y_insert: np.ndarray = np.ones((im_array.shape[0], bounds[1][1], im_array.shape[2])) * padded_color
        im_array = np.insert(im_array, [0], top_y_insert, axis = 1)
        im_array = np.append(im_array, bot_y_insert, axis = 1)
        front_z_insert: np.ndarray = np.ones((bounds[0][0], im_array.shape[1], im_array.shape[2])) * padded_color
        back_z_insert: np.ndarray = np.ones((bounds[0][1], im_array.shape[1], im_array.shape[2])) * padded_color
        im_array = np.insert(im_array, [0], front_z_insert, axis = 0)
        im_array = np.append(im_array, back_z_insert, axis = 0)
        
    return im_array
    
def pad(im_array: np.ndarray, x_bounds: int | list[int] = None, y_bounds: int | list[int] = None, z_bounds: int | list[int] = None, *, bounds_dict: dict[str, list[int]] = None, bounds_as_slices: bool = False, padded_color: float | int = 0, conserve_mem: bool = False) -> np.ndarray:
    
    bounds = trim_pad_bounds(im_array, x_bounds, y_bounds, z_bounds, bounds_dict, bounds_as_slices, "pad")
    
    if conserve_mem:
        
        return pad_operation(im_array, bounds, padded_color)
    
    else:
        
        pad_array = np.copy(im_array)
        
        return pad_operation(pad_array, bounds, padded_color)

def remove_slice_coords(coords: np.ndarray) -> dict[str, np.ndarray]:
    
    if coords.shape[1] > 2:
        
        coords = np.transpose(np.array([coords[:, 1], coords[:, 2]]))
    
    return coords

def get_in_plane_dims(im_array: np.ndarray) -> tuple[int]:
    
    if len(im_array.shape) == 2:
        
        return (im_array.shape[0], im_array.shape[1])
    
    else:
        
        return (im_array.shape[1], im_array.shape[2])
    
def get_rot_angle(shape_dict: dict[str: np.ndarray]) -> float:
    
    shape_type: str = list(shape_dict.keys())[0]
    shape_coords: np.ndarray = shape_dict[shape_type]
    
    if shape_coords.shape[0] == 4 and shape_type != "polygon":

        rot_angle: float = -math.atan2((shape_coords[1, 0] - shape_coords[0, 0]), (shape_coords[1, 1] - shape_coords[0, 1]))
    
    else:
        
        rot_angle: float = 0
        
    return rot_angle

def shape_2_mask(im_array: np.ndarray, shape_dict: dict[str: np.ndarray]) -> np.ndarray:

    mask_shape: tuple[int] = get_in_plane_dims(im_array)
    mask_array: np.ndarray = np.zeros(mask_shape, dtype = np.bool)
    
    for shape in list(shape_dict.keys()):
        
        shape_coords: np.ndarray = shape_dict[shape]
        shape_type: str = shape[:shape.find("-")]
        
        if shape_type == "ellipse":
                
            rot_angle: float = get_rot_angle(shape_dict)
            r_radius: float = math.sqrt(((shape_coords[3, 0] - shape_coords[0, 0])**2) + ((shape_coords[3, 1] - shape_coords[0, 1])**2)) / 2
            c_radius: float = math.sqrt(((shape_coords[1, 0] - shape_coords[0, 0])**2) + ((shape_coords[1, 1] - shape_coords[0, 1])**2)) / 2
            r_center: float = shape_coords[0, 0] + ((shape_coords[2, 0] - shape_coords[0, 0]) / 2)
            c_center: float = shape_coords[0, 1] + ((shape_coords[2, 1] - shape_coords[0, 1]) / 2)
            rr, cc = draw.ellipse(r_center, c_center, r_radius, c_radius, shape = mask_shape, rotation = rot_angle)
            mask_array[rr, cc] = 1
                
        elif shape_type == "polygon" or shape_type == "rectangle":
                
            r_coords: np.ndarray = shape_coords[:, 0]
            c_coords: np.ndarray = shape_coords[:, 1]
            rr, cc = draw.polygon(r_coords, c_coords, shape = mask_shape)
            mask_array[rr, cc] = 1
            
    return mask_array

def project_mask(mask_array: np.ndarray, num_slices: int) -> np.ndarray:
    
    return np.repeat(np.expand_dims(mask_array, 0), num_slices, axis = 0)

def get_mask(im_array: np.ndarray, viewer: napari.viewer.Viewer, *, shapes_layer: napari.layers.Shapes = None, slice_range: tuple = None, convert_to_3d: bool = True) -> np.ndarray:
    
    shape_dict: dict[str, np.ndarray] = sv.extract_shapes(viewer, shapes_layer)
    
    for shape in list(shape_dict.keys()):
        
        shape_dict[shape] = remove_slice_coords(shape_dict[shape])
        
    mask_array: np.ndarray = shape_2_mask(im_array, shape_dict)
    
    if convert_to_3d:
        
        if slice_range:
            
            mask_array = project_mask(mask_array, max(slice_range) - min(slice_range))
            zero_shape = (mask_array.shape[1], mask_array.shape[2])
            
            if min(slice_range) != 0:
                
                zero_insert: np.ndarray = project_mask(np.zeros(zero_shape, mask_array.dtype), min(slice_range))
                mask_array = np.append(zero_insert, mask_array, axis = 0)
                
            if max(slice_range) != im_array.shape[0]:
                
                zero_insert: np.ndarray = project_mask(np.zeros(zero_shape, mask_array.dtype), (im_array.shape[0] - max(slice_range)))
                mask_array = np.append(mask_array, zero_insert, axis = 0)
            
        else:
        
            mask_array = project_mask(mask_array, im_array.shape[0])
    
    mask_array = np.bool(mask_array)
        
    return mask_array
    
def mask(im_array: np.ndarray, mask_array: np.ndarray, *, method: str = "out", mask_color: float | int = 0, conserve_mem: bool = False) -> np.ndarray:
    
    if len(mask_array.shape) < len(im_array.shape):
        
        mask_array = project_mask(mask_array, im_array.shape[0])
    
    if conserve_mem:
        
        if method == "out":
        
            im_array[np.logical_not(mask_array)] = mask_color
            
        elif method == "in":
            
            im_array[mask_array] = mask_color
        
        return im_array
    
    else:
        
        masked_array = np.copy(im_array)
        
        if method == "out":
        
            masked_array[np.logical_not(mask_array)] = mask_color
            
        else:
            
            masked_array[mask_array] = mask_color
        
        return masked_array
    
def quick_mask(im_array: np.ndarray, viewer: napari.viewer.Viewer, *, method: str = "out", mask_color: float | int = 0, conserve_mem: bool = False) -> np.ndarray:
    
    mask_array: np.ndarray = get_mask(im_array, viewer)
    
    return mask(im_array, mask_array, method = method, mask_color = mask_color, conserve_mem = conserve_mem)

def crop(im_array: np.ndarray, mask_array: np.ndarray, *, mask_color: float | int = 0, conserve_mem: bool = False) -> np.ndarray:
    
    if len(mask_array.shape) < len(im_array.shape):
        
        mask_array = project_mask(mask_array, im_array.shape[0])
    
    mask_indices: np.ndarray = remove_slice_coords(np.argwhere(mask_array == True))
    r_start: np.int64 = np.min(mask_indices[:, 0])
    c_start: np.int64 = np.min(mask_indices[:, 1])
    r_end: np.int64 = np.max(mask_indices[:, 0])
    c_end: np.int64 = np.max(mask_indices[:, 1])
    mask_array = mask_array[:, r_start:r_end, c_start:c_end]
    
    if conserve_mem:
        
        im_array = im_array[:, r_start:r_end, c_start:c_end]
        
        if not np.all(mask_array):
            
            im_array = mask(im_array, mask_array, mask_color = mask_color, conserve_mem = True)
        
        return im_array
    
    else:
        
        crop_array: np.ndarray = im_array[:, r_start:r_end, c_start:c_end]
        
        if not np.all(mask_array):
            
            crop_array = mask(crop_array, mask_array, mask_color = mask_color, conserve_mem = False)
        
        return crop_array

def quick_crop(im_array: np.ndarray, viewer: napari.viewer.Viewer, *, mask_color: float | int = 0, conserve_mem: bool = False) -> np.ndarray:
    
    mask_array: np.ndarray = get_mask(im_array, viewer)
    
    return crop(im_array, mask_array, mask_color = mask_color, conserve_mem = conserve_mem)

def mask_logic(mask_array1: np.ndarray, mask_array2: np.ndarray, method: str = "union") -> np.ndarray:
    
    if mask_array1.dtype != np.bool:
        
        proc_array1 = np.bool(mask_array1)
        
    else:
        
        proc_array1 = np.copy(mask_array1)
        
    if mask_array2.dtype != np.bool:
        
        proc_array2 = np.bool(mask_array2)
        
    else:
        
        proc_array2 = np.copy(mask_array2)
    
    if method == "union":
        
        return proc_array1 + proc_array2
    
    elif method == "subtract":
        
        proc_array1[proc_array2] = False
        
        return proc_array1
    
    elif method == "intersect":
        
        return proc_array1 & proc_array2


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()