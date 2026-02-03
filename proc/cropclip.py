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

def trim(im_array: np.ndarray, x_bounds: int | list[int] = None, y_bounds: int | list[int] = None, z_bounds: int | list[int] = None, *, bounds_dict: dict[str, list[int]] = None, bounds_as_slices: bool = False, conserve_mem: bool = False) -> np.ndarray:
    
    if im_array.ndim == 3:
        
        if im_array.shape[2] == 3:
            
            rgb: bool = True
            dim: int = 2
            
        else:
            
            rgb: bool = False
            dim: int = 3
        
    elif im_array.ndim == 4:
        
        rgb: bool = True
        dim: int = 3
        
    elif im_array.ndim == 2:
    
        rgb: bool = False
        dim: int = 2
        
    if bounds_dict:
        
        x_bounds = bounds_dict["X"]
        y_bounds = bounds_dict["Y"]
        z_bounds = bounds_dict["Z"]
            
    x_ax: int = util.convert_ax_str_to_int(im_array, rgb, "X")
    y_ax: int = util.convert_ax_str_to_int(im_array, rgb, "Y")
    x_bounds: list[int] = util.reformat_bounds(x_bounds, im_array.shape[x_ax], bounds_as_slices)
    y_bounds: list[int] = util.reformat_bounds(y_bounds, im_array.shape[y_ax], bounds_as_slices)
    bounds: dict[int, list] = {x_ax: x_bounds, y_ax: y_bounds}
    
    if dim == 3:
        
        z_ax: int = util.convert_ax_str_to_int(im_array, rgb, "Z")
        z_bounds: list[int] = util.reformat_bounds(z_bounds, im_array.shape[z_ax], bounds_as_slices)
        bounds[z_ax] = z_bounds
    
    if conserve_mem:
        
        if dim == 2:
                
            return im_array[bounds[0][0]:bounds[0][1], bounds[1][0]:bounds[1][1]]
                
        else:
                
            return im_array[bounds[0][0]:bounds[0][1], bounds[1][0]:bounds[1][1], bounds[2][0]:bounds[2][1]]
    
    else:
        
        if dim == 2:
                
            trim_array: np.ndarray = im_array[bounds[0][0]:bounds[0][1], bounds[1][0]:bounds[1][1]]
                
        else:
                
            trim_array: np.ndarray = im_array[bounds[0][0]:bounds[0][1], bounds[1][0]:bounds[1][1], bounds[2][0]:bounds[2][1]]
        
        return trim_array

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
    
    valid_shapes: tuple[str] = ("rectangle", "ellipse", "polygon")
    shape_type: str = list(shape_dict.keys())[0]
    shape_coords: np.ndarray = shape_dict[shape_type]
    
    if any(shape_type.find(x) != -1 for x in valid_shapes):
    
        mask_shape: tuple[int] = get_in_plane_dims(im_array)
        mask_array: np.ndarray = np.zeros(mask_shape, dtype = np.bool)
        
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
    
    else:
        
        print("\nInvalid shape type!")

def project_mask(mask_array: np.ndarray, num_slices: int) -> np.ndarray:
    
    return np.repeat(np.expand_dims(mask_array, 0), num_slices, axis = 0)

def get_mask(im_array: np.ndarray, viewer: napari.viewer.Viewer, *, convert_to_3d: bool = True) -> np.ndarray:
    
    shape_dict: dict[str, np.ndarray] = sv.extract_shapes(viewer)
    shape_dict[list(shape_dict.keys())[0]] = remove_slice_coords(shape_dict[list(shape_dict.keys())[0]])
    mask_array: np.ndarray = shape_2_mask(im_array, shape_dict)
    
    if convert_to_3d:
        
        return project_mask(mask_array, im_array.shape[0])
    
    else:
        
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

def pad(im_array: np.ndarray, bounds: np.ndarray, pad_method: str = "add", *, mode: str = "constant", constant: int | float = 0, dimensions_method: str = "split") -> np.ndarray:
    
    if pad_method == "dimensions":
        
        old_dims: tuple[int] = im_array.shape
        new_bounds: np.array = np.empty(len(old_dims))
        
        for index, bound in enumerate(bounds):
        
            if dimensions_method == "split":
                
                fore_val: int = int(math.ceil((bound - old_dims[index]) / 2))
                
            elif dimensions_method == "front":
                
                fore_val: int = bound - old_dims[index]
            
            elif dimensions_method == "rear":
                
                fore_val: int = 0
            
            rear_val: int = bound - old_dims[index] - fore_val
            new_bounds[index] = np.array([fore_val, rear_val])
            
        bounds = np.copy(new_bounds)
        
    if mode == "constant":
        
        return np.pad(im_array, bounds, mode = mode, constant_values = constant)
    
    else:
        
        return np.pad(im_array, bounds, mode = mode)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()