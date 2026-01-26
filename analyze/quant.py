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
from segment import thresh


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

def get_histogram(im_array: np.ndarray, *, mask_array: np.ndarray = None, normalize: bool = False) -> pd.DataFrame:
    
    if np.any(mask_array):
    
        counts, bin_centers = exposure.histogram(im_array[mask_array], normalize = normalize)
        
    else:
        
        counts, bin_centers = exposure.histogram(im_array, normalize = normalize)
        
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
    
def __vol_area_precondition(im_array: np.ndarray, *, include_background: bool = False, background: float | int = 0) -> np.ndarray:
    
    if im_array.dtype == np.int64:
        
        count_array: np.ndarray = np.array([255, np.count_nonzero(im_array > 0)])
        
    else:
        
        phase_array: np.ndarray = np.unique(im_array)
        
        if not include_background:
            
            phase_array = np.delete(phase_array, np.argwhere(phase_array == background))
        
        count_array: np.ndarray = np.empty(phase_array.shape)
        
        for index, phase in enumerate(phase_array):
            
            count_array[index] = np.count_nonzero(im_array == phase)
            
        count_array = np.stack((phase_array, count_array), 1)
            
    return count_array        
    
def get_volume(im_array: np.ndarray, *, scale: float = 1.0, units: str = "pix", include_background: bool = False, background: float | int = 0) -> pd.DataFrame:
    
    count_array = __vol_area_precondition(im_array, include_background = include_background, background = background)
    count_array[:, 1] = count_array[:, 1] * (scale ** 3)
    vol_df: pd.DataFrame = pd.DataFrame(count_array, columns = ["Gray Value", "Volume"])
    vol_df.attrs = {"units": f"{units}^3"}
    
    return vol_df

def get_area(im_array: np.ndarray, *, scale: float = 1.0, units: str = "pix", include_background: bool = False, background: float | int = 0) -> pd.DataFrame:
    
    count_array = __vol_area_precondition(im_array, include_background = include_background, background = background)
    count_array[:, 1] = count_array[:, 1] * (scale ** 2)
    area_df: pd.DataFrame = pd.DataFrame(count_array, columns = ["Gray Value", "Area"])
    area_df.attrs = {"units": f"{units}^2"}
    
    return area_df

def get_position_distribution(im_array: np.ndarray, *, mode: str = "vol", scale: float = 1.0, units: str = "pix", temporal_scale: float | int = None, temporal_units: str = "s", axis: int = 0, include_background: bool = False, background: float | int = 0) -> pd.DataFrame:
    
    if temporal_scale:
        
        pos_scale = temporal_scale
        pos_units = temporal_units
        
    else:
        
        pos_scale = scale
        pos_units = units
    
    phases: np.ndarray = np.unique(im_array)
    
    if not include_background:
        
        phases = np.delete(phases, np.argwhere(phases == background))
        
    pos_array: np.ndarray = np.empty((im_array.shape[axis], 1 + len(phases)))
    
    for slice_index in range(0, im_array.shape[axis]):
        
        pos_array[slice_index, 0] = slice_index * pos_scale
    
        if axis == 0:
            
            int_im_array: np.ndarray = im_array[slice_index]
            
        elif axis == 1:
            
            int_im_array: np.ndarray = im_array[:, slice_index, :]
        
        elif axis == 2:

            int_im_array: np.ndarray = im_array[:, :, slice_index]
            
        int_array: np.ndarray = __vol_area_precondition(int_im_array, include_background = include_background, background = background)
        
        for index, gray_value in enumerate(int_array[:, 0]):
            
            pos_array[slice_index, 1 + np.argwhere(phases == gray_value)] = int_array[index, 1]
            
    if temporal_scale:
        
        columns = ["Time"]
        
    else:
        
        columns = ["Position"]
    
    for phase in phases:
        
        columns.append(str(phase))
            
    if mode == "vol":
        
        pos_array[:, 1:] = pos_array[:, 1:] * (scale ** 3)
        pos_df: pd.DataFrame = pd.DataFrame(pos_array, columns = columns)
        
        if temporal_scale:
            
            pos_df.attrs = {"time_units": f"{pos_units}", "vol_units": f"{units}^3"}
            
        else:
            
            pos_df.attrs = {"pos_units": f"{pos_units}", "vol_units": f"{units}^3"}
        
    elif mode == "area":
        
        pos_array[:, 1:] = pos_array[:, 1:] * (scale ** 2)
        pos_df: pd.DataFrame = pd.DataFrame(pos_array, columns = columns)
        
        if temporal_scale:
            
            pos_df.attrs = {"time_units": f"{pos_units}", "area_units": f"{units}^2"}
            
        else:
            
            pos_df.attrs = {"pos_units": f"{pos_units}", "area_units": f"{units}^2"}
        
    return pos_df

def __get_size_distribution(im_array: np.ndarray, *, mode: str = "vol", scale: float = 1.0, units: str = "pix", background: float | int = 0) -> pd.DataFrame:
    
    counts, labels = exposure.histogram(im_array)        
    counts = np.delete(counts, np.argwhere(labels == background))
    size_counts, sizes = exposure.histogram(counts)
    
    if mode == "vol":
        
        sizes = sizes * (scale ** 3)
        
    elif mode == "area":
        
        sizes = sizes * (scale ** 2)
    
    size_df: pd.DataFrame = pd.DataFrame(np.stack((sizes, size_counts), 1), columns = ["Bin Centers", "Counts"])
    
    if mode == "vol":
        
        size_df.attrs = {"units": f"{units}^3"}
        
    elif mode == "area":
        
        size_df.attrs = {"units": f"{units}^2"}
        
    return size_df

def get_size_distribution(im_array: np.ndarray, *, mode: str = "vol", scale: float = 1.0, units: str = "pix", connectivity: int = None, background: float | int = 0, positional: bool = False, temporal_scale: float | int = None, temporal_units: str = "s") -> pd.DataFrame:
    
    if not positional:
    
        if im_array.dtype != np.int64:
            
            lab_array = thresh.label(im_array, connectivity = connectivity, background = background)
            size_df: pd.DataFrame = __get_size_distribution(lab_array, mode = mode, scale = scale, units = units, background = background)
            
        else:
            
            size_df: pd.DataFrame = __get_size_distribution(im_array, mode = mode, scale = scale, units = units, background = background)
            
        return size_df
    
    # else:
        
    #     if temporal_scale:
            
    #         pos_scale = temporal_scale
    #         pos_units = temporal_units
            
    #     else:
            
    #         pos_scale = scale
    #         pos_units = units
            
    #     if im_array.dtype != np.int64:
            
    #         lab_array = thresh.label(im_array, connectivity = connectivity, background = background, positional = True)
            
    #     for slice_index in range(0, im_array.shape[0]):
            
    #         if im_array.dtype != np.int64:
                
    #             int_im_array = lab_array[slice_index]
                
    #         else:
                
    #             int_im_array = im_array[slice_index]
                
    #         int_df: pd.DataFrame = __get_size_distribution(int_im_array, mode = mode, scale = scale, units = units, connectivity = connectivity, background = background)

def get_time_distribution(im_array: np.ndarray, mode: str = "vol", *, size_mode: str = "vol", scale: float = 1.0, spatial_units: str = "pix", temporal_units: str = "s", temporal_scale: float | int = 1.0, connectivity: int = None, axis: int = 0, include_background: bool = False, background: float | int = 0) -> pd.DataFrame:
    
    if mode == "size":
        
        time_df: pd.DataFrame = get_size_distribution(im_array, mode = size_mode, scale = scale, units = spatial_units, connectivity = connectivity, background = background, positional = True, temporal_scale = temporal_scale, temporal_units = temporal_units)
    
    elif mode == "vol":
        
        time_df: pd.DataFrame = get_position_distribution(im_array, mode = mode, scale = scale, units = spatial_units, temporal_units = temporal_units, temporal_scale = temporal_scale, axis = axis, include_background = include_background, background = background)

    elif mode == "area":
        
        time_df: pd.DataFrame = get_position_distribution(im_array, mode = mode, scale = scale, units = spatial_units, temporal_units = temporal_units, temporal_scale = temporal_scale, axis = axis, include_background = include_background, background = background)
    
    return time_df

def get_surface_area(im_array: np.ndarray, *, scale: float = 1.0, units: str = "pix") -> pd.DataFrame:
    
    pass

def get_contact_area(im_array: np.ndarray, *, scale: float = 1.0, units: str = "pix") -> pd.DataFrame:
    
    pass

def get_thick_map(im_array: np.ndarray, *, scale: float = 1.0, units: str = "pix", axis: int = 0) -> np.ndarray:
    
    pass

def get_height_map(im_array: np.ndarray, *, scale: float = 1.0, units: str = "pix", axis: int = 0) -> np.ndarray:
    
    pass


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()