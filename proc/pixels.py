"""
Module for altering and assessing pixel values and dimensions
"""

# Imports

import cropclip as cc
import numpy as np

from skimage import transform
from skimage import exposure
from skimage import util


# Functions

def statistics(im_array: np.array, *, shape_coords: np.array = None, shape_type: str = None) -> dict:
    
    im_stats: dict = {}
    
    if shape_type:
            
        mask_shape: tuple[int] = cc.get_in_plane_dims(im_array)
        coords_dict: dict[str, list] = cc.coords_2_lists(shape_coords)
        rot_angle: float = cc.get_rot_angle(shape_coords, shape_type)
        
        if shape_type == "rectangle":
            
            mask_dict: dict[str, list] = cc.rectangle_mask(mask_shape, coords_dict, rot_angle)
            
        elif shape_type == "ellipse":
            
            mask_dict: dict[str, list] = cc.ellipse_mask(mask_shape, coords_dict, rot_angle)
        
        elif shape_type == "polygon":
            
            mask_dict: dict[str, list] = cc.polygon_mask(mask_shape, coords_dict)
           
        if len(im_array.shape) == 3:
            
            mask_array: np.array = cc.mask_2d_to_3d(np.expand_dims(mask_dict["mask"], axis = 0), im_array.shape[0])
            
        else:
            
            mask_array: np.array = mask_dict["mask"]
        
        im_stats["mean"] = float(np.mean(im_array[mask_array]))
        im_stats["median"] = float(np.median(im_array[mask_array]))
        im_stats["min"] = float(np.min(im_array[mask_array]))
        im_stats["max"] = float(np.max(im_array[mask_array]))
        im_stats["stdev"] = float(np.std(im_array[mask_array]))

    else:
        
        im_stats["mean"] = float(np.mean(im_array))
        im_stats["median"] = float(np.median(im_array))
        im_stats["min"] = float(np.min(im_array))
        im_stats["max"] = float(np.max(im_array))
        im_stats["stdev"] = float(np.std(im_array))
    
    return im_stats

def saturate(im_array: np.array, bounds: tuple) -> np.array:
    
    im_array[im_array > max(bounds)] = max(bounds)
    im_array[im_array < min(bounds)] = min(bounds)
    
    return im_array

def normalize(im_array: np.array, norm_bounds: tuple) -> np.array:
    
    return np.astype((((im_array - im_array.min()) / (im_array.max() - im_array.min())) * (max(norm_bounds) - min(norm_bounds))) + min(norm_bounds), im_array.dtype)

def convert_im_type(im_array: np.array, convert_type: str, *, norm: bool = False, float_bounds: tuple[float] = None) -> np.array:
    
    valid_types: tuple[str] = ("uint8", "uint16", "int16", "float", "float32", "float64", "bool")
    
    if any(x == convert_type for x in valid_types):
        
        if str(im_array.dtype).find("float") != -1 and (norm or (np.max(im_array) > 1 or np.min(im_array) < 0)):
            
            if float_bounds:
                
                im_array = saturate(im_array, float_bounds);
            
            im_array = normalize(im_array, (0, 1))
            
        if convert_type == "uint8":
                    
            conv_array: np.array = util.img_as_ubyte(im_array)
                
        elif convert_type == "uint16":
                    
            conv_array: np.array = util.img_as_uint(im_array)
                
        elif convert_type == "int16":
                    
            conv_array: np.array = util.img_as_int(im_array)
                
        elif convert_type == "float":
                    
            conv_array: np.array = util.img_as_float(im_array)
                    
        elif convert_type == "float32":
                    
            conv_array: np.array = util.img_as_float32(im_array)
                    
        elif convert_type == "float64":
                    
            conv_array: np.array = util.img_as_float64(im_array)
                
        elif convert_type == "bool":
                    
            conv_array: np.array = util.img_as_bool(im_array)
            
        return conv_array
        
    else:
            
        print("\nInvalid convert type!")
        
def rescale(im_array: np.array, scale: float) -> np.array:
    
    if scale == 1:
        
        return im_array
    
    elif 1 > scale > 0:
        
        return convert_im_type(transform.rescale(im_array, scale, anti_aliasing = True), im_array.dtype)
    
    elif scale > 1:
        
        return convert_im_type(transform.rescale(im_array, scale), im_array.dtype)
    
    else:
        
        print("\nInvalid rescaling factor!")
        
def invert(im_array: np.array) -> np.array:
    
    return util.invert(im_array)

def histogram_equalization(im_array: np.array, method: str = "global", *, mask_array: np.array = None, kernel_size = None, clip_limit = 0.01) -> np.array:
    
    valid_methods: tuple[str] = ("global", "local")
    
    if any(x == method for x in valid_methods):
        
        if method == "global":
            
            if np.any(mask_array):
                
                if mask_array.shape != im_array.shape:
                    
                    mask_array = cc.mask_2d_to_3d(mask_array, im_array.shape[0])
            
            return convert_im_type(exposure.equalize_hist(im_array, mask = mask_array), im_array.dtype)
        
        elif method == "local":
            
            return convert_im_type(exposure.equalize_adapthist(im_array, kernel_size, clip_limit), im_array.dtype)
    
    else:
        
        print("\nInvalid histogram equalization method!")
        
def histogram_matching(im_array: np.array, ref_array: np.array) -> np.array:
    
    return convert_im_type(exposure.match_histograms(im_array, ref_array), im_array.dtype)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()