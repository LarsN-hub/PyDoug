"""
Module for altering pixel gray values
"""


# Imports

import pandas as pd
import numpy as np

from skimage import util as skutil, exposure, filters, color

from PyDoug.proc import cropclip as cc, util, morph
from PyDoug.analyze import distrib, quant


# Functions

def rgb_2_gray(im_array: np.ndarray) -> np.ndarray:
    
    if im_array.shape[-1] > 3:
        
        if im_array.ndim == 3:
            
            return convert_im_type(color.rgb2gray(im_array[:, :, 0:3]), "uint8")
        
        elif im_array.ndim == 4:
            
            return convert_im_type(color.rgb2gray(im_array[:, :, :, 0:3]), "uint8")
        
    else:
    
        return convert_im_type(color.rgb2gray(im_array), "uint8")
    
def labels_2_rgb(im_array: np.ndarray) -> np.ndarray:
    
    return convert_im_type(color.label2rgb(im_array), "uint8")

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
        
        if np.issubdtype(im_array.dtype, np.floating) and (norm or (np.max(im_array) > 1 or np.min(im_array) < 0)):
            
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

def equalize_histogram(im_array: np.ndarray, method: str = "global", *, mask_array: np.ndarray = None, clip_limit: float = 0.01, radius: int = 3, along_axis: bool = False, axis: int = 0) -> np.ndarray:
    
    if np.any(mask_array):
                
        if mask_array.shape != im_array.shape:
                    
            mask_array = cc.mask_2d_to_3d(mask_array, im_array.shape[0])
            
        mask_array = np.bool(mask_array)
            
    if along_axis:
        
        proc_array: np.ndarray = util.get_along_axis_array(im_array, axis)
        eq_array: np.ndarray = np.empty(proc_array.shape, proc_array.dtype)
        
        if np.any(mask_array):
            
            proc_mask_array: np.ndrray = util.get_along_axis_array(mask_array, axis)
        
        if method == "global":
            
            if np.any(mask_array):
            
                for n in range(0, proc_array.shape[0]):
                
                    if np.any(proc_mask_array[n]):
                        
                        eq_array[n] = convert_im_type(exposure.equalize_hist(proc_array[n], mask = proc_mask_array[n]), im_array.dtype)
                        
                    else:
                        
                        eq_array[n] = proc_array[n]
                    
            else:
                
                for n in range(0, proc_array.shape[0]):
                
                    eq_array[n] = convert_im_type(exposure.equalize_hist(proc_array[n]), im_array.dtype)
            
        elif method == "local":
            
            disk = morph.Footprint("disk")
            disk.radius = radius
            footprint = disk.get_footprint()
                
            if im_array.ndim == 2:
                    
                eq_array = filters.rank.equalize(proc_array, footprint = footprint, mask = mask_array)
                    
            else:
                
                if np.any(mask_array):
                
                    for n in range(0, proc_array.shape[0]):
                        
                        if np.any(proc_mask_array[n]):
                
                            eq_array[n] = filters.rank.equalize(proc_array[n], footprint = footprint, mask = proc_mask_array[n])
                            
                        else:
                            
                            eq_array[n] = proc_array[n]
                        
                else:
                    
                    for n in range(0, proc_array.shape[0]):
                
                        eq_array[n] = filters.rank.equalize(proc_array[n], footprint = footprint)
                        
        elif method == "adaptive":
            
            for n in range(0, proc_array.shape[0]):
                
                eq_array[n] = convert_im_type(exposure.equalize_adapthist(proc_array[n], radius, clip_limit), im_array.dtype)
        
        return util.undo_axial_array(eq_array, axis)
    
    else:
                
        if method == "global":
                
            return convert_im_type(exposure.equalize_hist(im_array, mask = mask_array), im_array.dtype)
            
        elif method == "local":
                
            if im_array.ndim == 2:
                    
                disk = morph.Footprint("disk")
                disk.radius = radius
                footprint = disk.get_footprint()
                    
            else:
                    
                ball = morph.Footprint("ball")
                ball.radius = radius
                footprint = ball.get_footprint()
                
            return filters.rank.equalize(im_array, footprint = footprint, mask = mask_array)
            
        elif method == "adaptive":
                
            return convert_im_type(exposure.equalize_adapthist(im_array, radius, clip_limit), im_array.dtype)
        
def histogram_matching(im_array: np.ndarray, ref_array: np.ndarray) -> np.ndarray:
    
    return convert_im_type(exposure.match_histograms(im_array, ref_array), im_array.dtype)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()