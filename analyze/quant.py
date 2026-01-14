"""
Module for analysis of segmented images
"""

# Imports

import numpy as np
import util

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

def get_histogram(im_array: np.ndarray, *, mask_array: np.ndarray = None) -> dict[str, np.ndarray]:
    
    if np.any(mask_array):
    
        counts, bin_centers = exposure.histogram(im_array[mask_array])
        
    else:
        
        counts, bin_centers = exposure.histogram(im_array)
        
    bin_centers = np.astype(bin_centers, im_array.dtype)
    
    return {"counts": counts, "bin centers": bin_centers}

def get_cdf(im_array: np.ndarray, *, mask_array: np.ndarray = None) -> dict[str, np.ndarray]:
    
    if np.any(mask_array):
    
        im_cdf, bin_centers = exposure.cumulative_distribution(im_array[mask_array])
        
    else:
        
        im_cdf, bin_centers = exposure.cumulative_distribution(im_array)
        
    bin_centers = np.astype(bin_centers, im_array.dtype)
        
    return {"cdf": im_cdf, "bin centers": bin_centers}

def get_percent_intensities(im_array: np.ndarray, percentages: tuple, *, mask_array: np.ndarray = None, cdf_dict: dict = None) -> tuple:
    
    if max(percentages) > 1:
        
        percentages = (percentages[0] / 100, percentages[1] / 100)
        
    if not cdf_dict:
        
        cdf_dict: dict = get_cdf(im_array, mask_array = mask_array)
        
    im_cdf: np.ndarray = cdf_dict["cdf"]
    bin_centers: np.ndarray = cdf_dict["bin centers"]
    low_index = util.quick_get_first_index(im_cdf, min(percentages), "greater or equal")
    high_index = len(im_cdf) - util.quick_get_first_index(np.flip(im_cdf, 0), max(percentages), "less or equal") - 1
    low_bin = np.astype(bin_centers[low_index], im_array.dtype)
    high_bin = np.astype(bin_centers[high_index], im_array.dtype)
    
    return (low_bin, high_bin)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()