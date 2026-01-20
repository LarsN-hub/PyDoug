"""
Module for threshold-based image segmentation
"""

# Imports

import numpy as np

from skimage import segmentation
from skimage import filters


# Functions

def sort_double_bound_thresholds(thresholds: np.ndarray) -> np.ndarray:
    
    threshold_sums: np.ndarray = np.sum(thresholds, 1)
    sorted_sums = np.sort(threshold_sums)
    new_thresholds: np.ndarray = np.empty([len(thresholds), 2], thresholds.dtype)
    
    for index, current_sum in enumerate(sorted_sums):
        
        new_thresholds[index] = thresholds[np.where(threshold_sums == current_sum)]
        
    return new_thresholds

def threshold(im_array: np.ndarray, thresholds: np.ndarray, inclusivity: str = "upper") -> np.ndarray:
    
    valid_methods: tuple[str] = ("upper", "lower", "both", "neither")
    
    if any(x == inclusivity for x in valid_methods):
    
        seg_array = np.zeros(im_array.shape, np.uint8)
        
        if len(thresholds.shape) == 0 and (inclusivity == "upper" or inclusivity == "lower"):
            
            if inclusivity == "upper":
            
                seg_array[im_array > thresholds] = 255
                
            elif inclusivity == "lower":
                
                seg_array[im_array >= thresholds] = 255
    
        if len(thresholds.shape) == 1 and (inclusivity == "upper" or inclusivity == "lower"):
            
            thresholds: np.ndarray = np.sort(thresholds)
            
            for index, thresh in enumerate(thresholds, start = 1):
                
                if inclusivity == "upper":
                
                    seg_array[im_array > thresh] = round((255 / len(thresholds)) * index)
                    
                elif inclusivity == "lower":
                    
                    seg_array[im_array >= thresh] = round((255 / len(thresholds)) * index)
        
        elif len(thresholds.shape) == 2:
            
            thresholds = sort_double_bound_thresholds(thresholds)
            
            for index, thresh in enumerate(thresholds, start = 1):
                
                if inclusivity == "upper":
                
                    seg_array[(im_array > np.min(thresh)) & (im_array <= np.max(thresh))] = round((255 / len(thresholds)) * index)
                    
                elif inclusivity == "lower":
                    
                    seg_array[(im_array >= np.min(thresh)) & (im_array < np.max(thresh))] = round((255 / len(thresholds)) * index)
                    
                elif inclusivity == "both":
                    
                    seg_array[(im_array >= np.min(thresh)) & (im_array <= np.max(thresh))] = round((255 / len(thresholds)) * index)
                    
                elif inclusivity == "neither":
                    
                    seg_array[(im_array > np.min(thresh)) & (im_array < np.max(thresh))] = round((255 / len(thresholds)) * index)
                
        return seg_array
    
    else:
        
        print("\nInvalid inclusivity method!")

def otsu(im_array: np.ndarray, num_classes: int = 2, *, return_thresholds = False) -> np.ndarray:
    
    if num_classes == 2:
        
        if return_thresholds:
            
            return threshold(im_array, filters.threshold_otsu(im_array)), filters.threshold_otsu(im_array)
        
        else:
        
            return threshold(im_array, filters.threshold_otsu(im_array))
        
    else:
        
        if return_thresholds:
            
            return threshold(im_array, filters.threshold_multiotsu(im_array, num_classes)), filters.threshold_multiotsu(im_array, num_classes)
        
        else:
        
            return threshold(im_array, filters.threshold_multiotsu(im_array, num_classes))

def watershed(seg_array: np.ndarray, *, markers = None, connectivity = 1) -> np.ndarray:
    
    return segmentation.watershed(seg_array, markers = markers, connectivity = connectivity)

def cluster(im_array: np.ndarray) -> np.ndarray:
    
    pass


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()