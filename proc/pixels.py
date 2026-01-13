"""
Module for altering and assessing pixel values and dimensions
"""

# Imports

import cropclip as cc
import numpy as np
import quant
import util

from skimage import util as skutil
from skimage import transform
from skimage import exposure


# Functions

def statistics(im_array: np.ndarray, *, mask_array: np.ndarray = None) -> dict:
    
    im_stats: dict = {}
    
    if np.any(mask_array):
            
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

def get_percent_intensities(im_array: np.ndarray, percentages: tuple, *, mask_array: np.ndarray = None, cdf_dict: dict = None) -> tuple:
    
    if max(percentages) > 1:
        
        percentages = (percentages[0] / 100, percentages[1] / 100)
        
    if not cdf_dict:
        
        cdf_dict: dict = quant.get_cdf(im_array, mask_array = mask_array)
        
    im_cdf: np.ndarray = cdf_dict["cdf"]
    bin_centers: np.ndarray = cdf_dict["bin centers"]
    low_index = util.quick_get_first_index(im_cdf, min(percentages), "greater or equal")
    high_index = len(im_cdf) - util.quick_get_first_index(np.flip(im_cdf, 0), max(percentages), "less or equal") - 1
    low_bin = np.astype(bin_centers[low_index], im_array.dtype)
    high_bin = np.astype(bin_centers[high_index], im_array.dtype)
    
    return (low_bin, high_bin)

def saturate(im_array: np.ndarray, bounds: tuple, *, bounds_percent: bool = True, mask_array: np.ndarray = None, cdf_dict: dict = None, conserve_mem: bool = False) -> np.ndarray:
    
    if bounds_percent:
        
        bounds = get_percent_intensities(im_array, bounds, mask_array = mask_array, cdf_dict = cdf_dict)
        
    if conserve_mem:
        
        im_array[im_array > max(bounds)] = max(bounds)
        im_array[im_array < min(bounds)] = min(bounds)
    
        return im_array
    
    else:
        
        sat_array = np.copy(im_array)
        sat_array[im_array > max(bounds)] = max(bounds)
        sat_array[im_array < min(bounds)] = min(bounds)
        
        return sat_array

def normalize(im_array: np.ndarray, norm_bounds: tuple) -> np.ndarray:
    
    return np.astype((((im_array - im_array.min()) / (im_array.max() - im_array.min())) * (max(norm_bounds) - min(norm_bounds))) + min(norm_bounds), im_array.dtype)

def convert_im_type(im_array: np.ndarray, convert_type: str, *, norm: bool = False, float_bounds: tuple[float] = None) -> np.ndarray:
    
    valid_types: tuple[str] = ("uint8", "uint16", "int16", "float", "float32", "float64", "bool")
    
    if any(x == convert_type for x in valid_types):
        
        if str(im_array.dtype).find("float") != -1 and (norm or (np.max(im_array) > 1 or np.min(im_array) < 0)):
            
            if float_bounds:
                
                im_array = saturate(im_array, float_bounds);
            
            im_array = normalize(im_array, (0, 1))
            
        if convert_type == "uint8":
                    
            conv_array: np.ndarray = skutil.img_as_ubyte(im_array)
                
        elif convert_type == "uint16":
                    
            conv_array: np.ndarray = skutil.img_as_uint(im_array)
                
        elif convert_type == "int16":
                    
            conv_array: np.ndarray = skutil.img_as_int(im_array)
                
        elif convert_type == "float":
                    
            conv_array: np.ndarray = skutil.img_as_float(im_array)
                    
        elif convert_type == "float32":
                    
            conv_array: np.ndarray = skutil.img_as_float32(im_array)
                    
        elif convert_type == "float64":
                    
            conv_array: np.ndarray = skutil.img_as_float64(im_array)
                
        elif convert_type == "bool":
                    
            conv_array: np.ndarray = skutil.img_as_bool(im_array)
            
        return conv_array
        
    else:
            
        print("\nInvalid convert type!")
        
def rescale(im_array: np.ndarray, scale: float) -> np.ndarray:
    
    if scale == 1:
        
        return im_array
    
    elif 1 > scale > 0:
        
        return convert_im_type(transform.rescale(im_array, scale, anti_aliasing = True), im_array.dtype)
    
    elif scale > 1:
        
        return convert_im_type(transform.rescale(im_array, scale), im_array.dtype)
    
    else:
        
        print("\nInvalid rescaling factor!")
        
def invert(im_array: np.ndarray) -> np.ndarray:
    
    return skutil.invert(im_array)

def histogram_equalization(im_array: np.ndarray, method: str = "global", *, mask_array: np.ndarray = None, kernel_size = None, clip_limit = 0.01) -> np.ndarray:
    
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
        
def histogram_matching(im_array: np.ndarray, ref_array: np.ndarray) -> np.ndarray:
    
    return convert_im_type(exposure.match_histograms(im_array, ref_array), im_array.dtype)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()