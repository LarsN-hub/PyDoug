"""
Module for quantified analysis of segmented images
"""

# Imports

import numpy as np
import util

from skimage import restoration
from skimage import exposure


# Functions

def statistics(im_array: np.ndarray, *, mask_array: np.ndarray = None) -> dict:
    
    im_stats: dict = {}
    
    if np.any(mask_array):
            
        im_stats["mean"] = np.mean(im_array[mask_array])
        im_stats["median"] = np.median(im_array[mask_array])
        im_stats["min"] = np.min(im_array[mask_array])
        im_stats["max"] = np.max(im_array[mask_array])
        im_stats["stdev"] = np.std(im_array[mask_array])

    else:
        
        im_stats["mean"] = np.mean(im_array)
        im_stats["median"] = np.median(im_array)
        im_stats["min"] = np.min(im_array)
        im_stats["max"] = np.max(im_array)
        im_stats["stdev"] = np.std(im_array)
    
    return im_stats

def single_ax_statistics(im_array: np.ndarray, axis: int = 0, *, mask_array: np.ndarray = None) -> dict:
    
    ax_stats: dict = {}
    
    if np.any(mask_array):
        
        ax_stats["mean"] = np.empty(im_array.shape[axis])
        ax_stats["median"] = np.empty(im_array.shape[axis])
        ax_stats["min"] = np.empty(im_array.shape[axis])
        ax_stats["max"] = np.empty(im_array.shape[axis])
        ax_stats["stdev"] = np.empty(im_array.shape[axis])
        
        if axis == 0:
        
            for slice_index in range(0, im_array.shape[axis]):
                
                if np.any(mask_array[slice_index]):
                    
                    ax_stats["mean"][slice_index] = np.mean(im_array[slice_index][mask_array[slice_index]])
                    ax_stats["median"][slice_index] = np.median(im_array[slice_index][mask_array[slice_index]])
                    ax_stats["min"][slice_index] = np.min(im_array[slice_index][mask_array[slice_index]])
                    ax_stats["max"][slice_index] = np.max(im_array[slice_index][mask_array[slice_index]])
                    ax_stats["stdev"][slice_index] = np.std(im_array[slice_index][mask_array[slice_index]])
                    
                else:
                    
                    ax_stats["mean"][slice_index] = 0
                    ax_stats["median"][slice_index] = 0
                    ax_stats["min"][slice_index] = 0
                    ax_stats["max"][slice_index] = 0
                    ax_stats["stdev"][slice_index] = 0
                
        elif axis == 1:
            
            for slice_index in range(0, im_array.shape[axis]):
                
                if np.any(mask_array[:, slice_index, :]):
                
                    ax_stats["mean"][slice_index] = np.mean(im_array[:, slice_index, :][mask_array[:, slice_index, :]])
                    ax_stats["median"][slice_index] = np.median(im_array[:, slice_index, :][mask_array[:, slice_index, :]])
                    ax_stats["min"][slice_index] = np.min(im_array[:, slice_index, :][mask_array[:, slice_index, :]])
                    ax_stats["max"][slice_index] = np.max(im_array[:, slice_index, :][mask_array[:, slice_index, :]])
                    ax_stats["stdev"][slice_index] = np.std(im_array[:, slice_index, :][mask_array[:, slice_index, :]])
                    
                else:
                    
                    ax_stats["mean"][slice_index] = 0
                    ax_stats["median"][slice_index] = 0
                    ax_stats["min"][slice_index] = 0
                    ax_stats["max"][slice_index] = 0
                    ax_stats["stdev"][slice_index] = 0
                
        elif axis == 2:
            
            for slice_index in range(0, im_array.shape[axis]):
                
                if np.any(mask_array[:, :, slice_index]):
                
                    ax_stats["mean"][slice_index] = np.mean(im_array[:, :, slice_index][mask_array[:, :, slice_index]])
                    ax_stats["median"][slice_index] = np.median(im_array[:, :, slice_index][mask_array[:, :, slice_index]])
                    ax_stats["min"][slice_index] = np.min(im_array[:, :, slice_index][mask_array[:, :, slice_index]])
                    ax_stats["max"][slice_index] = np.max(im_array[:, :, slice_index][mask_array[:, :, slice_index]])
                    ax_stats["stdev"][slice_index] = np.std(im_array[:, :, slice_index][mask_array[:, :, slice_index]])
                    
                else:
                    
                    ax_stats["mean"][slice_index] = 0
                    ax_stats["median"][slice_index] = 0
                    ax_stats["min"][slice_index] = 0
                    ax_stats["max"][slice_index] = 0
                    ax_stats["stdev"][slice_index] = 0
    
    else:
        
        if axis == 0:
            
            exclude_axes: tuple = (1, 2)
            
        elif axis == 1:
            
            exclude_axes: tuple = (0, 2)
            
        elif axis == 2:
            
            exclude_axes: tuple = (0, 1)
        
        ax_stats["mean"] = np.mean(im_array, exclude_axes)
        ax_stats["median"] = np.median(im_array, exclude_axes)
        ax_stats["min"] = np.min(im_array, exclude_axes)
        ax_stats["max"] = np.max(im_array, exclude_axes)
        ax_stats["stdev"] = np.std(im_array, exclude_axes)
    
    ax_stats["position"] = np.arange(0, len(ax_stats["mean"]))
    
    return ax_stats

def axial_statistics(im_array: np.ndarray, *, mask_array = None) -> dict:
    
    axial_stats: dict = {}
    axial_stats[0] = single_ax_statistics(im_array, 0, mask_array = mask_array)
    axial_stats[1] = single_ax_statistics(im_array, 1, mask_array = mask_array)
    axial_stats[2] = single_ax_statistics(im_array, 2, mask_array = mask_array)
    
    return axial_stats

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

def linear_cdf(cdf_dict: dict, percent_interval: float = 0.1, *, mask_array: np.ndarray = None) -> dict[str, np.ndarray]:
    
    interval_array: np.ndarray = np.arange(0, 1, (percent_interval / 100))
    linear_indices: np.ndarray = util.quick_get_indices(cdf_dict["cdf"], interval_array)
    
    return {"cdf": interval_array, "bin centers": cdf_dict["bin centers"][np.astype(linear_indices, "int")]}

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

def estimate_noise(im_array: np.ndarray) -> float:
    
    return restoration.estimate_sigma(im_array)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()