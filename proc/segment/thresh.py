"""
Module for threshold-based image segmentation
"""


# Imports

import cropclip as cc
import pandas as pd
import numpy as np
import distrib
import pixels
import util

from filtering import morph
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

def gui_threshold(im_array: np.ndarray, thresholds: tuple[float, int]) -> np.ndarray:
    
    thresh_array = np.zeros(im_array.shape, np.uint8)
    thresh_array[(im_array >= min(thresholds)) & (im_array <= max(thresholds))] = 255
    
    return thresh_array

def threshold(im_array: np.ndarray, thresholds: float | int| np.ndarray, inclusivity: str = "upper") -> np.ndarray:
    
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
        
        return filters.threshold_minimum(hist = hist)
    
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
    
def local(im_array: np.ndarray, *, mask_array: np.ndarray = None, method = "adaptive", radius: int = 3, window_size: int = 15, k: float = 0.2, r: float = None) -> np.ndarray:
    
    if radius % 2 == 0:
        
        radius -= 1
        
    if window_size % 2 == 0:
        
        window_size -= 1
    
    if method == "adaptive":
        
        return pixels.convert_im_type((im_array > filters.threshold_local(im_array, block_size = radius)), "uint8")
    
    elif method == "niblack":
        
        return pixels.convert_im_type((im_array > filters.threshold_niblack(im_array, window_size, k)), "uint8")
    
    elif method == "sauvola":
        
        return pixels.convert_im_type((im_array > filters.threshold_sauvola(im_array. window_size, k, r)), "uint8")
    
    elif method == "rank":
        
        if im_array.ndim == 2:
                
            disk = morph.Footprint("disk")
            disk.radius = radius
            footprint = disk.get_footprint()
                
        else:
                
            ball = morph.Footprint("ball")
            ball.radius = radius
            footprint = ball.get_footprint()
        
        return pixels.convert_im_type(pixels.normalize(filters.rank.threshold(im_array, footprint, mask = mask_array)), "uint8")
    
def label(im_array: np.ndarray, *, mask_array: np.ndarray = None, connectivity: int = None, return_num: bool = False, background: float | int = 0, positional: bool = False, axis: int = 0, randomize: bool = True) -> np.ndarray | int:
    
    proc_array: np.ndarray = np.copy(im_array)
    
    if np.any(mask_array):
        
        if mask_array.ndim > im_array.ndim:
            
            mask_array = cc.project_mask(mask_array, im_array.shape[0])
            
        proc_array[np.logical_not(np.bool(mask_array))] = background
    
    if not positional:
    
        if not connectivity:
            
            if im_array.ndim > 2:
                
                connectivity = 3
                
            else:
                
                connectivity = 2
                
        lab_array: np.ndarray = measure.label(proc_array, background = background, return_num = return_num, connectivity = connectivity)

    else:
        
        if not connectivity:
            
            connectivity = 2
            
        proc_array = util.get_along_axis_array(im_array, axis)
        lab_array: np.ndarray = np.empty(proc_array.shape, dtype = np.int64)
        num_unique: np.ndarray = np.empty(proc_array.shape[0])
        
        for slice_index in range(0, proc_array.shape[0]):
            
            lab_array[slice_index], num_unique[slice_index] = measure.label(proc_array[slice_index], background = background, connectivity = connectivity, return_num = True)
        
        if return_num:
            
            lab_array = util.undo_axial_array(lab_array, axis), num_unique
        
        else:
            
            lab_array = util.undo_axial_array(lab_array, axis)
            
    if randomize:
        
        return randomize_labels(lab_array)
    
    else:
        
        return lab_array
        
def randomize_labels(im_array: np.ndarray) -> np.ndarray:
    
    labels: np.ndarray = np.unique(im_array)[1:]
    rng: np.random.Generator = np.random.default_rng()
    rand_labels: np.ndarray = np.copy(labels)
    rng.shuffle(rand_labels)
    rand_array: np.ndarray = np.zeros(im_array.shape, im_array.dtype)
    
    for index, og_label in enumerate(labels):
        
        rand_array[im_array == og_label] = rand_labels[index]
        
    return rand_array
        

# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()