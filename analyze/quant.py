"""
Module for quantified analysis of segmented images
"""

# Imports

import pandas as pd
import numpy as np
import distrib
import util

from filtering import denoising
from skimage import restoration
from skimage import feature
from typing import Callable


# Functions

def estimate_noise(im_array: np.ndarray) -> float:
    
    return restoration.estimate_sigma(im_array)

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

def get_percent_intensities(im_array: np.ndarray, percentages: tuple, *, mask_array: np.ndarray = None, cdf_dict: dict = None) -> tuple:
    
    if max(percentages) > 1:
        
        percentages = (percentages[0] / 100, percentages[1] / 100)
        
    if not cdf_dict:
        
        cdf_dict: dict = distrib.get_cdf(im_array, mask_array = mask_array)
        
    im_cdf: np.ndarray = cdf_dict["cdf"]
    bin_centers: np.ndarray = cdf_dict["bin centers"]
    low_index = util.quick_get_first_index(im_cdf, min(percentages), "greater or equal")
    high_index = len(im_cdf) - util.quick_get_first_index(np.flip(im_cdf, 0), max(percentages), "less or equal") - 1
    low_bin = np.astype(bin_centers[low_index], im_array.dtype)
    high_bin = np.astype(bin_centers[high_index], im_array.dtype)
    
    return (low_bin, high_bin)

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
    
def __vol_area_precondition(im_array: np.ndarray, *, mask_array: np.ndarray = None, include_background: bool = False, background: float | int = 0) -> np.ndarray:
    
    if im_array.dtype == np.int64:
        
        if np.any(mask_array):
        
            count_array: np.ndarray = np.expand_dims(np.array([255, np.count_nonzero(im_array[mask_array] > 0)]), 0)
            
            if include_background:
                
                count_array = np.vstack((np.array([0, np.count_nonzero(im_array[mask_array] == 0)]), count_array))
            
        else:
            
            count_array: np.ndarray = np.expand_dims(np.array([255, np.count_nonzero(im_array > 0)]), 0)
            
            if include_background:
                
                count_array = np.vstack((np.array([0, np.count_nonzero(im_array == 0)]), count_array))
        
    else:
        
        phase_array: np.ndarray = np.unique(im_array)
        
        if not include_background:
            
            phase_array = np.delete(phase_array, np.argwhere(phase_array == background))
        
        count_array: np.ndarray = np.empty(phase_array.shape)
        
        for index, phase in enumerate(phase_array):
            
            if np.any(mask_array):
                
                count_array[index] = np.count_nonzero(im_array[mask_array] == phase)
            
            else:
            
                count_array[index] = np.count_nonzero(im_array == phase)
            
        count_array = np.stack((phase_array, count_array), 1)
            
    return count_array        
    
def get_volume(im_array: np.ndarray, *, mask_array: np.ndarray = None, scale: float = 1.0, units: str = "pix", include_background: bool = False, background: float | int = 0) -> pd.DataFrame:
    
    count_array = __vol_area_precondition(im_array, mask_array = mask_array, include_background = include_background, background = background)
    count_array[:, 1] = count_array[:, 1] * (scale ** 3)
    vol_df: pd.DataFrame = pd.DataFrame(count_array, columns = ["Gray Value", "Volume"])
    vol_df.attrs = {"units": f"{units}\u00b3"}
    
    return vol_df

def get_area(im_array: np.ndarray, *, mask_array: np.ndarray = None, scale: float = 1.0, units: str = "pix", include_background: bool = False, background: float | int = 0) -> pd.DataFrame:
    
    count_array = __vol_area_precondition(im_array, mask_array = mask_array, include_background = include_background, background = background)
    count_array[:, 1] = count_array[:, 1] * (scale ** 2)
    area_df: pd.DataFrame = pd.DataFrame(count_array, columns = ["Gray Value", "Area"])
    area_df.attrs = {"units": f"{units}\u00b2"}
    
    return area_df

def __contact_include(pix1: float | int, pix2: float | int, phase_ints: tuple[float, int]) -> bool:
    
    if not isinstance(phase_ints, tuple):
    
        if pix1 != pix2:
            
            return True
        
        else:
            
            return False
        
    else:
        
        if pix1 != pix2 and any(pix1 == x for x in phase_ints) and any(pix2 == x for x in phase_ints):
            
            return True
        
        else:
            
            return False

def __get_contact_counts(im_array: np.ndarray, phase_ints: tuple[float, int], *, include_edges: bool = False) -> pd.DataFrame:
    
    counts: int = 0
    
    for c in range(0, im_array.shape[1]):
        
        for r in range(0, im_array.shape[0]):
            
            if r == 0:
                
                if include_edges and im_array[r, c] in phase_ints:
                
                    counts += 1
                    
            else:
                
                if __contact_include(im_array[r, c], im_array[(r - 1), c], phase_ints):
                    
                    counts += 1
                    
                if r == im_array.shape[0] - 1 and include_edges:
                    
                    if im_array[r, c] in phase_ints:
                        
                        counts += 1
        
    return counts

def get_contact_perimeter(im_array: np.ndarray, phase_ints: tuple[float, int] | float | int = None, *, pixel_size: float | int = 1.0, units: str = "pix", include_edges: bool = False) -> pd.DataFrame:
    
    if not phase_ints:
        
        phase_ints = np.max(im_array)
        
    counts: int = __get_contact_counts(im_array, phase_ints, include_edges = include_edges)
    counts += __get_contact_counts(im_array.T, phase_ints, include_edges = include_edges)
    per_df: pd.DataFrame = pd.DataFrame({"Gray Values": [str(phase_ints)], "Perimeter": [counts * pixel_size]})
    per_df.attrs = {"units": f"{units}"}
    
    return per_df

def get_contact_area(im_array: np.ndarray, phase_ints: tuple[float, int], *, pixel_size: float | int = 1.0, units: str = "pix", total_surface_area: bool = False, include_edges: bool = False) -> pd.DataFrame:
    
    if not phase_ints:
        
        phase_ints = np.max(im_array)
        
    counts: int = 0
        
    for slice_index in range(0, im_array.shape[0]):
        
        counts += __get_contact_counts(im_array[slice_index], phase_ints, include_edges = include_edges)
        
    for row_index in range(0, im_array.shape[1]):
        
        counts += __get_contact_counts(im_array[:, row_index, :], phase_ints, include_edges = include_edges)
        
    for col_index in range(0, im_array.shape[2]):
        
        counts += __get_contact_counts(im_array[:, :, col_index], phase_ints, include_edges = include_edges)
    
    if not isinstance(phase_ints, tuple):
        
        area_df: pd.DataFrame = pd.DataFrame({"Gray Values": [str(phase_ints)], "Surface Area": [counts * (pixel_size ** 2)]})
        
    else:
        
        area_df: pd.DataFrame = pd.DataFrame({"Gray Values": [str(phase_ints)], "Contact Area": [counts * (pixel_size ** 2)]})
        
    area_df.attrs = {"units": f"{units}\u00b2"}
    
    return area_df

def get_thick_map(im_array: np.ndarray, *, pixel_size: float = 1.0, units: str = "pix", axis: int = 0) -> np.ndarray:
    
    pass

def get_height_map(im_array: np.ndarray, *, pixels_size: float = 1.0, units: str = "pix", axis: int = 0) -> np.ndarray:
    
    pass


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()