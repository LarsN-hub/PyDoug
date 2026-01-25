"""
Module for quantified analysis of segmented images
"""

# Imports

import pandas as pd
import numpy as np
import util

from filtering import denoising
from skimage import restoration
from skimage import exposure
from skimage import feature
from typing import Callable


# Functions

def global_statistics(im_array: np.ndarray, *, mask_array: np.ndarray = None) -> pd.DataFrame:
    
    im_stats: dict = {}
    
    if np.any(mask_array):
            
        im_stats["Mean"] = np.mean(im_array[mask_array])
        im_stats["Median"] = np.median(im_array[mask_array])
        im_stats["Min"] = np.min(im_array[mask_array])
        im_stats["Max"] = np.max(im_array[mask_array])
        im_stats["Std Dev"] = np.std(im_array[mask_array])

    else:
        
        im_stats["Mean"] = np.mean(im_array)
        im_stats["Median"] = np.median(im_array)
        im_stats["Min"] = np.min(im_array)
        im_stats["Max"] = np.max(im_array)
        im_stats["Std Dev"] = np.std(im_array)
    
    return pd.DataFrame([im_stats])

def single_ax_statistics(im_array: np.ndarray, axis: int = 0, *, mask_array: np.ndarray = None) -> pd.DataFrame:
    
    ax_stats: np.ndarray = np.empty((im_array.shape[axis], 6))
    
    if np.any(mask_array):
        
        if axis == 0:
        
            for slice_index in range(0, im_array.shape[axis]):
                
                ax_stats[slice_index, 0] = slice_index
                
                if np.any(mask_array[slice_index]):

                    ax_stats[slice_index, 1] = np.mean(im_array[slice_index][mask_array[slice_index]])
                    ax_stats[slice_index, 2] = np.median(im_array[slice_index][mask_array[slice_index]])
                    ax_stats[slice_index, 3] = np.min(im_array[slice_index][mask_array[slice_index]])
                    ax_stats[slice_index, 4] = np.max(im_array[slice_index][mask_array[slice_index]])
                    ax_stats[slice_index, 5] = np.std(im_array[slice_index][mask_array[slice_index]])
                    
                else:
                    
                    ax_stats[slice_index, 1] = 0
                    ax_stats[slice_index, 2] = 0
                    ax_stats[slice_index, 3] = 0
                    ax_stats[slice_index, 4] = 0
                    ax_stats[slice_index, 5] = 0
                
        elif axis == 1:
            
            for slice_index in range(0, im_array.shape[axis]):
                
                ax_stats[slice_index, 0] = slice_index
                
                if np.any(mask_array[:, slice_index, :]):
                
                    ax_stats[slice_index, 1] = np.mean(im_array[:, slice_index, :][mask_array[:, slice_index, :]])
                    ax_stats[slice_index, 2] = np.median(im_array[:, slice_index, :][mask_array[:, slice_index, :]])
                    ax_stats[slice_index, 3] = np.min(im_array[:, slice_index, :][mask_array[:, slice_index, :]])
                    ax_stats[slice_index, 4] = np.max(im_array[:, slice_index, :][mask_array[:, slice_index, :]])
                    ax_stats[slice_index, 5] = np.std(im_array[:, slice_index, :][mask_array[:, slice_index, :]])
                    
                else:
                    
                    ax_stats[slice_index, 1] = 0
                    ax_stats[slice_index, 2] = 0
                    ax_stats[slice_index, 3] = 0
                    ax_stats[slice_index, 4] = 0
                    ax_stats[slice_index, 5] = 0
                
        elif axis == 2:
            
            for slice_index in range(0, im_array.shape[axis]):
                
                ax_stats[slice_index, 0] = slice_index
                
                if np.any(mask_array[:, :, slice_index]):
                
                    ax_stats[slice_index, 1] = np.mean(im_array[:, :, slice_index][mask_array[:, :, slice_index]])
                    ax_stats[slice_index, 2] = np.median(im_array[:, :, slice_index][mask_array[:, :, slice_index]])
                    ax_stats[slice_index, 3] = np.min(im_array[:, :, slice_index][mask_array[:, :, slice_index]])
                    ax_stats[slice_index, 4] = np.max(im_array[:, :, slice_index][mask_array[:, :, slice_index]])
                    ax_stats[slice_index, 5] = np.std(im_array[:, :, slice_index][mask_array[:, :, slice_index]])
                    
                else:
                    
                    ax_stats[slice_index, 1] = 0
                    ax_stats[slice_index, 2] = 0
                    ax_stats[slice_index, 3] = 0
                    ax_stats[slice_index, 4] = 0
                    ax_stats[slice_index, 5] = 0
    
    else:
        
        if axis == 0:
            
            exclude_axes: tuple = (1, 2)
            
        elif axis == 1:
            
            exclude_axes: tuple = (0, 2)
            
        elif axis == 2:
            
            exclude_axes: tuple = (0, 1)
        
        ax_stats[:, 0] = np.arange(0, im_array.shape[axis])
        ax_stats[:, 1] = np.mean(im_array, exclude_axes)
        ax_stats[:, 2] = np.median(im_array, exclude_axes)
        ax_stats[:, 3] = np.min(im_array, exclude_axes)
        ax_stats[:, 4] = np.max(im_array, exclude_axes)
        ax_stats[:, 5] = np.std(im_array, exclude_axes)
    
    return pd.DataFrame(ax_stats, columns = ["Position", "Mean", "Median", "Min", "Max", "Std Dev"])

def axial_statistics(im_array: np.ndarray, *, mask_array = None) -> dict[int, pd.DataFrame]:
    
    axial_stats: dict[int, pd.DataFrame] = {}
    axial_stats[0] = single_ax_statistics(im_array, 0, mask_array = mask_array)
    axial_stats[1] = single_ax_statistics(im_array, 1, mask_array = mask_array)
    axial_stats[2] = single_ax_statistics(im_array, 2, mask_array = mask_array)
    
    return axial_stats

def get_histogram(im_array: np.ndarray, *, mask_array: np.ndarray = None) -> pd.DataFrame:
    
    if np.any(mask_array):
    
        counts, bin_centers = exposure.histogram(im_array[mask_array])
        
    else:
        
        counts, bin_centers = exposure.histogram(im_array)
        
    bin_centers = np.astype(bin_centers, im_array.dtype)
    
    return pd.DataFrame(np.stack((bin_centers, counts), 1), columns = ["Bin Centers", "Counts"])

def get_cdf(im_array: np.ndarray, *, mask_array: np.ndarray = None) -> pd.DataFrame:
    
    if np.any(mask_array):
    
        im_cdf, bin_centers = exposure.cumulative_distribution(im_array[mask_array])
        
    else:
        
        im_cdf, bin_centers = exposure.cumulative_distribution(im_array)
        
    bin_centers = np.astype(bin_centers, im_array.dtype)
        
    return pd.DataFrame(np.stack((bin_centers, im_cdf), 1), columns = ["Bin Centers", "Probability"])

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

def get_denoising_losses(im_array: np.ndarray, denoiser: Callable[[np.ndarray], np.ndarray],
                         parameters: dict[str, np.ndarray], *,
                         stride: int = 4, approximate_loss: bool = True) -> dict[str, list]:
    
    _, (parameters_tested, losses) = denoising.calibrate_function(im_array, denoiser, parameters, stride = stride,
                                                                  approximate_loss = approximate_loss,
                                                                  extra_output = True,
                                                                  return_type = "function")
    
    return {"parameters": parameters_tested, "losses": losses}

def get_corner_orientations(im_array: np.ndarray, corners: np.ndarray, mask_array: np.ndarray = None) -> np.ndarray:
    
    if not mask_array:
        
        mask_array: np.ndarray = np.ones((5, 5))
    
    if len(im_array.shape) > 2:
        
        output_array: np.ndarray = np.empty((corners.shape[0], 2))
        output_array[:, 0] = corners[:, 0]
        slices: np.ndarray = np.unique(corners[:, 0])
        
        for slice_index in slices:
            
            start_row: np.int64 = np.where(corners[:, 0] == slice_index)[0][0]
            end_row: np.int64 = np.where(corners[:, 0] == slice_index)[0][-1]
            output_array[start_row:end_row, 1] = feature.corner_orientations(im_array[slice_index], corners[start_row:end_row, 1:2], mask_array)
            
        return output_array
            
    else:
        
        return feature.corner_orientations(im_array, corners, mask_array)
    
def get_volume(im_array: np.ndarray, *, scale: float = 1.0, units: str = "pixels", include_background: bool = False, background: float | int = 0) -> pd.DataFrame:
    
    phase_array: np.ndarray = np.unique(im_array)
    
    if not include_background:
        
        phase_array = np.delete(phase_array, np.argwhere(phase_array == background))
    
    vol_array: np.ndarray = np.empty(phase_array.shape)
    
    for index, phase in enumerate(phase_array):
        
        vol_array[index] = np.count_nonzero(im_array == phase) * (scale ** 3)
        
    vol_df: pd.DataFrame = pd.DataFrame(np.stack((phase_array, vol_array), 1), columns = ["Gray Value", "Volume"])
    vol_df.attrs = {"units": f"{units}^3"}
    
    return vol_df
    
def get_size_distribution(im_array: np.ndarray, *, scale: float = 1.0, units: str = "pixels", connectivity: int = None) -> pd.DataFrame:
    
    pass

def get_volume_distribution(im_array: np.ndarray, *, scale: float = 1.0, units: str = "pixels", axis: int = 0) -> pd.DataFrame:
    
    pass

def get_surface_area(im_array: np.ndarray, *, scale: float = 1.0, units: str = "pixels") -> pd.DataFrame:
    
    pass

def get_contact_area(im_array: np.ndarray, *, scale: float = 1.0, units: str = "pixels") -> pd.DataFrame:
    
    pass

def get_thick_map(im_array: np.ndarray, *, scale: float = 1.0, units: str = "pixels", axis: int = 0) -> np.ndarray:
    
    pass

def get_height_map(im_array: np.ndarray, *, scale: float = 1.0, units: str = "pixels", axis: int = 0) -> np.ndarray:
    
    pass


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()