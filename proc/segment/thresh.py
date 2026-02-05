"""
Module for threshold-based image segmentation
"""

# Imports

import cropclip as cc
import pandas as pd
import numpy as np
import distrib
import pixels

from skimage import filters
from skimage import measure


# Functions

def sort_double_bound_thresholds(thresholds: np.ndarray) -> np.ndarray:
    
    threshold_sums: np.ndarray = np.sum(thresholds, 1)
    sorted_sums = np.sort(threshold_sums)
    new_thresholds: np.ndarray = np.empty([len(thresholds), 2], thresholds.dtype)
    
    for index, current_sum in enumerate(sorted_sums):
        
        new_thresholds[index] = thresholds[np.where(threshold_sums == current_sum)]
        
    return new_thresholds

def threshold(im_array: np.ndarray, thresholds: float | int| np.ndarray, inclusivity: str = "upper") -> np.ndarray:
    
    valid_methods: tuple[str] = ("upper", "lower", "both", "neither")
    
    if any(x == inclusivity for x in valid_methods):
        
        if not isinstance(thresholds, np.ndarray):
            
            thresholds = np.array(thresholds)
    
        thresh_array = np.zeros(im_array.shape, np.uint8)
        
        if len(thresholds.shape) == 0:
            
            if inclusivity == "lower":
                
                thresh_array[im_array >= thresholds] = 255
                
            else:
                
                thresh_array[im_array > thresholds] = 255
    
        if len(thresholds.shape) == 1:
            
            thresholds: np.ndarray = np.sort(thresholds)
            
            for index, thresh in enumerate(thresholds, start = 1):
                
                if inclusivity == "lower":
                    
                    thresh_array[im_array >= thresh] = round((255 / len(thresholds)) * index)
                    
                else:
                    
                    thresh_array[im_array > thresh] = round((255 / len(thresholds)) * index)
        
        elif thresholds.ndim == 2:
            
            thresholds = sort_double_bound_thresholds(thresholds)
            
            for index, thresh in enumerate(thresholds, start = 1):
                
                if inclusivity == "upper":
                
                    thresh_array[(im_array > np.min(thresh)) & (im_array <= np.max(thresh))] = round((255 / len(thresholds)) * index)
                    
                elif inclusivity == "lower":
                    
                    thresh_array[(im_array >= np.min(thresh)) & (im_array < np.max(thresh))] = round((255 / len(thresholds)) * index)
                    
                elif inclusivity == "both":
                    
                    thresh_array[(im_array >= np.min(thresh)) & (im_array <= np.max(thresh))] = round((255 / len(thresholds)) * index)
                    
                elif inclusivity == "neither":
                    
                    thresh_array[(im_array > np.min(thresh)) & (im_array < np.max(thresh))] = round((255 / len(thresholds)) * index)
                
        return thresh_array
    
    else:
        
        print("\nInvalid inclusivity method!")
    
def hist_thresholds(data: np.ndarray | pd.DataFrame, *, method: str = "otsu", otsu_classes: int = 2, mask_array: np.ndarray = None) -> np.float64 | np.int64 | np.ndarray:
    
    if isinstance(data, np.ndarray):
        
        if np.any(mask_array):
            
            if mask_array.ndim < data.ndim:
                
                mask_array = cc.mask_2d_to_3d(mask_array, data.shape[0])
        
        hist_df: pd.DataFrame = distrib.get_histogram(data, mask_array = mask_array)
        
    else:
        
        hist_df = data.copy()
    
    hist: tuple[np.ndarray] = (np.array(hist_df["Counts"]), np.array(hist_df["Bin Centers"]))
    
    if method == "otsu":
        
        if otsu_classes == 2:
            
            return filters.threshold_otsu(hist = hist)
        
        else:
            
            return filters.threshold_multiotsu(classes = otsu_classes, hist = hist)
        
    elif method == "isodata":
        
        return filters.threshold_isodata(hist = hist)
    
    elif method == "li":
        
        return filters.threshold_isodata(data)
    
    elif method == "mean":
        
        return filters.threshold_mean(data)
    
    elif method == "minimum":
        
        return filters.threhsold_minimum(hist = hist)
    
    elif method == "triangle":
        
        return filters.threshold_triangle(data)
    
    elif method == "yen":
        
        return filters.threshold_yen(hist = hist)
    
def hist(im_array: np.ndarray, *, method: str = "otsu", otsu_classes: int = 2, mask_array: np.ndarray = None, return_thresholds: bool = False) -> np.ndarray | np.float64 | np.int64:
    
    thresholds: np.float64 | np.int64 | np.ndarray = hist_thresholds(im_array, otsu_classes = otsu_classes, mask_array = mask_array, method = method)
    
    if return_thresholds:
        
        return threshold(im_array, thresholds), thresholds
    
    else:
    
        return threshold(im_array, thresholds)
    
def local(im_array: np.ndarray, *, mask_array: np.ndarray = None, method = "adaptive", block_size: int = 3, window_size: int = 15, k: float = 0.2, r: float = None) -> np.ndarray:
    
    if block_size % 2 == 0:
        
        block_size -= 1
        
    if window_size % 2 == 0:
        
        window_size -= 1
    
    if method == "adaptive":
        
        return pixels.convert_im_type((im_array > filters.threshold_local(im_array, block_size = block_size)), "uint8")
    
    elif method == "niblack":
        
        return pixels.convert_im_type((im_array > filters.threshold_niblack(im_array, window_size, k)), "uint8")
    
    elif method == "sauvola":
        
        return pixels.convert_im_type((im_array > filters.threshold_sauvola(im_array. window_size, k, r)), "uint8")
    
def label(im_array: np.ndarray, *, mask_array: np.ndarray = None, connectivity: int = None, return_num: bool = False, background: float | int = 0, positional: bool = False, axis: int = 0) -> np.ndarray | int:
    
    if np.any(mask_array):
        
        if mask_array.ndim > im_array.ndim:
            
            mask_array = cc.project_mask(mask_array, im_array.shape[0])
    
    if not positional:
    
        if not connectivity:
            
            if im_array.ndim > 2:
                
                connectivity = 3
                
            else:
                
                connectivity = 2
                
        lab_array: np.ndarray = measure.label(im_array, background = background, return_num = return_num, connectivity = connectivity)
        
        if np.any(mask_array):
            
            lab_array[mask_array] = 0
            
        return lab_array

    else:
        
        if not connectivity:
            
            connectivity = 2
            
        lab_array: np.ndarray = np.empty(im_array.shape, dtype = np.int64)
        num_unique: np.ndarray = np.empty(im_array.shape[axis])
        
        for slice_index in range(0, im_array.shape[axis]):
            
            if axis == 0:
                
                lab_array[slice_index], num_unique[slice_index] = measure.label(im_array[slice_index], background = background, connectivity = connectivity, return_num = True)
                    
            elif axis == 1:
                
                lab_array[:, slice_index, :], num_unique[slice_index] = measure.label(im_array[:, slice_index, :], background = background, connectivity = connectivity, return_num = True)
            
            elif axis == 2:
                
                lab_array[:, :, slice_index], num_unique[slice_index] = measure.label(im_array[:, :, slice_index], background = background, connectivity = connectivity, return_num = True)
            
            if np.any(mask_array):
                
                lab_array[mask_array] = 0
        
        if return_num:
            
            return lab_array, num_unique
        
        else:
            
            return lab_array
        

# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()