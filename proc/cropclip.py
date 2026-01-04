"""
Module for cropping, clipping, and padding image dimensions
"""

# Imports

import numpy as np
import math

from skimage import draw


# Functions

def get_in_plane_dims(im_array: np.array) -> tuple[int]:
    
    if len(im_array.shape) == 2:
        
        return (im_array.shape[0], im_array.shape[1])
    
    else:
        
        return (im_array.shape[1], im_array.shape[2])

def coords_2_lists(shape_coords: np.array) -> dict[str, list]:
    
    shape_coords = np.rint(shape_coords)
    rows: list[int] = []
    cols: list[int] = []
    
    for index, coords in enumerate(shape_coords):
        
        if len(coords) > 2:
            
            rows.append(int(coords[1]))
            cols.append(int(coords[2]))
        
        else:
            
            rows.append(int(coords[0]))
            cols.append(int(coords[1]))
        
    return {"rows": rows, "cols": cols}

def rectangle_mask(mask_shape: tuple[int], coords_dict: dict[str, list], rot_angle: float = 0) -> dict[str, np.array, tuple]:
    
    mask_array: np.array = np.zeros(mask_shape, dtype = np.bool)
    
    if rot_angle:
        
        r_coords = np.array(coords_dict["rows"])
        c_coords = np.array(coords_dict["cols"])
        rr, cc = draw.polygon(r_coords, c_coords, shape = mask_shape)
        mask_array[rr, cc] = 1
    
    else:
        
        if len(coords_dict["rows"]) == 2:
        
            orig_coords: tuple[int] = (coords_dict["rows"][0], coords_dict["cols"][0])
            oppo_coords: tuple[int] = (coords_dict["rows"][1], coords_dict["cols"][1])
            
        else:
            
            orig_coords: tuple[int] = (coords_dict["rows"][0], coords_dict["cols"][0])
            oppo_coords: tuple[int] = (coords_dict["rows"][2], coords_dict["cols"][2])
            
        rr, cc = draw.rectangle(orig_coords, oppo_coords, shape = mask_shape)
        mask_array[rr, cc] = 1
        
    return get_mask_dict(mask_array, rr, cc)

def ellipse_mask(mask_shape: tuple[int], coords_dict: dict[str, list], rot_angle: float = 0) -> dict[str, np.array, tuple]:
    
    mask_array: np.array = np.zeros(mask_shape, dtype = np.bool)
    orig_coords: tuple[int] = (coords_dict["rows"][0], coords_dict["cols"][0])
    next_coords: tuple[int] = (coords_dict["rows"][1], coords_dict["cols"][1])
    oppo_coords: tuple[int] = (coords_dict["rows"][2], coords_dict["cols"][2])
    prev_coords: tuple[int] = (coords_dict["rows"][3], coords_dict["cols"][3])
    r_radius: float = math.sqrt(((prev_coords[0] - orig_coords[0])**2) + ((prev_coords[1] - orig_coords[1])**2)) / 2
    c_radius: float = math.sqrt(((next_coords[0] - orig_coords[0])**2) + ((next_coords[1] - orig_coords[1])**2)) / 2
    r_center: float = orig_coords[0] + ((oppo_coords[0] - orig_coords[0]) / 2)
    c_center: float = orig_coords[1] + ((oppo_coords[1] - orig_coords[1]) / 2)
    rr, cc = draw.ellipse(r_center, c_center, r_radius, c_radius, shape = mask_shape, rotation = rot_angle)
    mask_array[rr, cc] = 1
        
    return get_mask_dict(mask_array, rr, cc)

def get_mask_dict(mask_array: np.array, rr: np.array, cc: np.array) -> dict[str, np.array, tuple]:
    
    low_coords: tuple[int] = (np.min(rr), np.min(cc))
    high_coords: tuple[int] = (np.max(rr), np.max(cc))
    
    return {"mask": mask_array, "start": low_coords, "end": high_coords}

def coords_2_mask(im_array: np.array, shape_coords: np.array, shape_type: str) -> dict[str, np.array, tuple]:
    
    valid_shapes: tuple[str] = ("rectangle", "ellipse", "polygon")
    
    if any(shape_type.find(x) != -1 for x in valid_shapes):
    
        mask_shape: tuple[int] = get_in_plane_dims(im_array)
        coords_dict: dict[str, list] = coords_2_lists(shape_coords)
        
        if len(coords_dict["rows"]) == 4 and shape_type != "polygon":

            orig_coords: tuple[int] = (coords_dict["rows"][0], coords_dict["cols"][0])
            next_coords: tuple[int] = (coords_dict["rows"][1], coords_dict["cols"][1])
            rot_angle: float = -math.atan2((next_coords[0] - orig_coords[0]), (next_coords[1] - orig_coords[1]))
        
        elif len(coords_dict["rows"]) == 2 and shape_type == "rectangle":
            
            rot_angle: float = 0
            
        else:
            
            r_coords = np.array(coords_dict["rows"])
            c_coords = np.array(coords_dict["cols"])
        
        if shape_type == "rectangle":
            
            mask_dict: dict[str, np.array, tuple] = rectangle_mask(mask_shape, coords_dict, rot_angle)
        
        elif shape_type == "ellipse":
            
            mask_dict: dict[str, np.array, tuple] = ellipse_mask(mask_shape, coords_dict, rot_angle)
            
        elif shape_type == "polygon":
            
            rr, cc = draw.polygon(r_coords, c_coords, shape = mask_shape)
            mask_array: np.array = np.zeros(mask_shape, dtype = np.bool)
            mask_array[rr, cc] = 1
            mask_dict: dict[str, np.array, tuple] = get_mask_dict(mask_array, rr, cc)
            
        return mask_dict
    
    else:
        
        print("\nInvalid shape type!")
        
def mask(im_array: np.array, shape_type: str, shape_coords: np.array, *, mask_method: str = "out", outside_mask_int: int | float = 0, conserve_mem: bool = False, return_mask: bool = False) -> np.array:
    
    valid_shapes: tuple[str] = ("rectangle", "ellipse", "polygon")
    
    if any(shape_type.find(x) != -1 for x in valid_shapes):
        
        mask_dict: dict[str, np.array, tuple] = coords_2_mask(im_array, shape_coords, shape_type)
        mask_array = np.expand_dims(mask_dict["mask"], 0)
        
        if conserve_mem:
            
            if len(im_array.shape) > 2:
                
                if mask_method == "out":
                    
                    im_array[np.logical_not(np.repeat(mask_array, im_array.shape[0], axis = 0))] = outside_mask_int
                    
                elif mask_method == "in":
                    
                    im_array[np.repeat(mask_array, im_array.shape[0], axis = 0)] = outside_mask_int
                
            else:
                
                if mask_method == "out":
                                    
                    im_array[np.logical_not(mask_dict["mask"])] = outside_mask_int
                    
                elif mask_method == "in":
                    
                    im_array[mask_dict["mask"]] = outside_mask_int
                
            if return_mask:
                
                return im_array, mask_dict
            
            else:
                
                return im_array
        
        else:
            
            masked_array: np.array = np.copy(im_array)
            
            if len(im_array.shape) > 2:
                
                if mask_method == "out":
                
                    masked_array[np.logical_not(np.repeat(mask_array, im_array.shape[0], axis = 0))] = outside_mask_int
                    
                elif mask_method == "in":
                    
                    masked_array[np.repeat(mask_array, im_array.shape[0], axis = 0)] = outside_mask_int
                
            else:
                
                if mask_method == "out":
                
                    masked_array[np.logical_not(mask_dict["mask"])] = outside_mask_int
                    
                elif mask_method == "in":
                    
                    masked_array[mask_dict["mask"]] = outside_mask_int
        
            if return_mask:
                
                return masked_array, mask_dict
            
            else:
                
                return masked_array
    
    else:
        
        print("\nInvalid shape type!")

def crop(im_array: np.array, shape_type: str, shape_coords: np.array, *, outside_mask_int: int | float = 0, conserve_mem: bool = False) -> np.array:
    
    valid_shapes: tuple[str] = ("rectangle", "ellipse", "polygon")
    
    if any(shape_type.find(x) != -1 for x in valid_shapes):
        
        if conserve_mem:
            
            im_array, mask_dict = mask(im_array, shape_type, shape_coords, outside_mask_int = outside_mask_int, conserve_mem = True, return_mask = True)
            low_coords: tuple = mask_dict["start"]
            high_coords: tuple = mask_dict["end"]
        
            return im_array[:, low_coords[0]:high_coords[0], low_coords[1]:high_coords[1]]
        
        else:
            
            crop_array: np.array = np.copy(im_array)
            
            if len(im_array.shape) > 2:
                
                crop_array, mask_dict = mask(crop_array, shape_type, shape_coords, outside_mask_int = outside_mask_int, conserve_mem = True, return_mask = True)
                low_coords: tuple = mask_dict["start"]
                high_coords: tuple = mask_dict["end"]
                
            else:
                
                crop_array[np.logical_not(mask_dict["mask"], axis = 0)] = outside_mask_int
        
            return crop_array[:, low_coords[0]:high_coords[0], low_coords[1]:high_coords[1]]
    
    else:
        
        print("\nInvalid shape type!")
        
def trim(im_array: np.array, bounds: np.array) -> np.array:
    
    return im_array[bounds[0][0]:bounds[0][1], bounds[1][0]:bounds[1][1], bounds[2][0]:bounds[2][1]]

def pad(im_array: np.array, bounds: np.array, pad_method: str = "add", *, mode: str = "constant", constant: int | float = 0, dimensions_method: str = "split") -> np.array:
    
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