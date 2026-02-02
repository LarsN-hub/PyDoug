"""
Module for altering and assessing pixel values and dimensions
"""

# Imports

import cropclip as cc
import pandas as pd
import numpy as np
import distrib
import quant

from skimage import util as skutil
from skimage import transform
from skimage import exposure
from skimage import filters
from filtering import morph


# Functions

def normalize(im_array: np.ndarray, *, in_range: tuple | str = None, out_range: tuple | str = None) -> np.ndarray:
     
    if in_range:
        
        if out_range:
            
            return exposure.rescale_intensity(im_array, in_range, out_range)
        
        else:
            
            return exposure.rescale_intensity(im_array, in_range, "dtype")
    
    else:
        
        if out_range:
            
            return exposure.rescale_intensity(im_array, "image", out_range)
        
        else:
            
            return exposure.rescale_intensity(im_array, "image", "dtype")

def saturate(im_array: np.ndarray, bounds: tuple, *, auto_normalize: bool = True, bounds_as_percents: bool = True, mask_array: np.ndarray = None, cdf_df: pd.DataFrame = None, conserve_mem: bool = False) -> np.ndarray:
    
    if bounds_as_percents:
        
        if np.any(cdf_df):
            
            cdf_df: pd.DataFrame = distrib.get_cdf(im_array, mask_array = mask_array)
        
        bounds = quant.get_percent_intensities(im_array, bounds, mask_array = mask_array, cdf_df = cdf_df)
        
    if conserve_mem:
        
        im_array[im_array > max(bounds)] = max(bounds)
        im_array[im_array < min(bounds)] = min(bounds)
    
        if auto_normalize:
            
            return normalize(im_array)
        
        else:
            
            return im_array
    
    else:
        
        sat_array = np.copy(im_array)
        sat_array[im_array > max(bounds)] = max(bounds)
        sat_array[im_array < min(bounds)] = min(bounds)
        
        if auto_normalize:
            
            return normalize(sat_array)
        
        else:
            
            return sat_array

def convert_im_type(im_array: np.ndarray, convert_type: str, *, norm: bool = False, float_bounds: tuple[float] = None) -> np.ndarray:
    
    valid_types: tuple[str] = ("uint8", "uint16", "int16", "float", "float32", "float64", "bool")
    
    if any(x == convert_type for x in valid_types):
        
        if str(im_array.dtype).find("float") != -1 and (norm or (np.max(im_array) > 1 or np.min(im_array) < 0)):
            
            if float_bounds:
                
                im_array = saturate(im_array, float_bounds);
            
            im_array = normalize(im_array, out_range = (0, 1))
            
        elif norm:
            
            im_array = normalize(im_array)
            
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
        
def invert(im_array: np.ndarray) -> np.ndarray:
    
    return skutil.invert(im_array)

def equalize_histogram(im_array: np.ndarray, method: str = "global", *, mask_array: np.ndarray = None, kernel_size: int | np.ndarray = None, clip_limit: float = 0.01, radius: int = 5) -> np.ndarray:
    
    valid_methods: tuple[str] = ("global", "local", "adaptive")
    
    if any(x == method for x in valid_methods):
        
        if np.any(mask_array):
                
            if mask_array.shape != im_array.shape:
                    
                mask_array = cc.mask_2d_to_3d(mask_array, im_array.shape[0])
                
        if method == "global":
            
            return convert_im_type(exposure.equalize_hist(im_array, mask = mask_array), im_array.dtype)
        
        elif method == "local":
            
            if len(im_array.shape) == 2:
                
                disk = morph.Footprint("disk")
                disk.radius = radius
                footprint = disk.get_footprint()
                
            else:
                
                ball = morph.Footprint("ball")
                ball.radius = radius
                footprint = ball.get_footprint()
            
            return filters.rank.equalize(im_array, footprint = footprint, mask = mask_array)
        
        elif method == "adaptive":
            
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