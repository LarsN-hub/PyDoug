"""
Module for single-value measurements of images
"""


# Imports

import pandas as pd
import numpy as np

from skimage import feature
from typing import Callable

from PyDoug.analyze import distrib
from PyDoug.proc import cropclip as cc, util, denoising


# Functions

def global_statistics(im_array: np.ndarray, *,
                      mask_array: np.ndarray = None,
                      print_results: bool = True) -> pd.DataFrame:
    
    im_stats: dict = {}
    
    if np.any(mask_array):
        
        if mask_array.ndim < im_array.ndim:
            
            mask_array = cc.project_mask(mask_array, im_array.shape[0])
            
        mask_array = np.bool(mask_array)
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
        
    dtype_dict = util.get_dtype_info(im_array)
    im_stats["DType Min"] = dtype_dict["Min"]
    im_stats["DType Max"] = dtype_dict["Max"]
    
    if print_results:
    
        for index, stat in enumerate(list(im_stats.keys())):
        
            current_str: str = stat + ":"
            
            if index == 0:
                
                print(f"\n{current_str:<16} {im_stats[stat]}")
                
            else:
                
                print(f"{current_str:<16} {im_stats[stat]}")
    
    return pd.DataFrame([im_stats])

def single_ax_statistics(im_array: np.ndarray, axis: int = 0, *,
                         mask_array: np.ndarray = None) -> pd.DataFrame:
    
    ax_stats: np.ndarray = np.empty((im_array.shape[axis], 6))
    
    if np.any(mask_array):
        
        if mask_array.ndim < im_array.ndim:
            
            mask_array = cc.project_mask(mask_array, im_array.shape[0])
        
        mask_array = np.bool(mask_array)
        
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

def get_percent_intensities(im_array: np.ndarray, percentages: tuple, *,
                            mask_array: np.ndarray = None,
                            cdf_df: pd.DataFrame = None) -> tuple:
    
    if max(percentages) > 1:
        
        percentages = (percentages[0] / 100, percentages[1] / 100)
    
    if not np.any(cdf_df):
        
        cdf_df: pd.DataFrame = distrib.get_cdf(im_array, mask_array = mask_array)
    
    im_cdf: pd.Series = np.squeeze(np.array([cdf_df["Probability"]]))
    bin_centers: pd.Series = np.squeeze(np.array([cdf_df["Bin Centers"]]))
    low_index = util.quick_get_first_index(im_cdf, min(percentages), "greater or equal")
    
    if not low_index:
        
        low_index = 0
        
    high_sub: int = util.quick_get_first_index(np.flip(im_cdf, 0), max(percentages), "less or equal")
    
    if not high_sub:
        
        high_sub = 0
        
    high_index = len(im_cdf) - 1 - high_sub
    low_bin = np.astype(bin_centers[low_index], im_array.dtype)
    high_bin = np.astype(bin_centers[high_index], im_array.dtype)
    low_str: str = str(min(percentages) * 100) + "%:"
    high_str: str = str(max(percentages) * 100) + "%:"
    print(f"\n{low_str:<16} {low_bin}")
    print(f"{high_str:<16} {high_bin}")
    
    return (low_bin, high_bin)

def get_denoising_losses(im_array: np.ndarray, denoiser: Callable[[np.ndarray],np.ndarray],
                         parameters: dict[str, np.ndarray], *,
                         stride: int = 4,
                         approximate_loss: bool = True) -> dict[str, list]:
    
    _, (parameters_tested, losses) = denoising.calibrate_function(im_array, denoiser, parameters, stride = stride,
                                                                  approximate_loss = approximate_loss,
                                                                  extra_output = True,
                                                                  return_type = "function")
    
    return {"parameters": parameters_tested, "losses": losses}

def get_corner_orientations(im_array: np.ndarray,
                            corners: np.ndarray,
                            mask_array: np.ndarray = None) -> np.ndarray:
    
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
    
def __vol_area_precondition(im_array: np.ndarray, *,
                            mask_array: np.ndarray = None,
                            include_background: bool = False,
                            background: float | int = 0,
                            normalize: bool = False) -> np.ndarray:
    
    if im_array.dtype == np.int64:
        
        if np.any(mask_array):
            
            if mask_array.ndim < im_array.ndim:
                
                mask_array = cc.project_mask(mask_array, im_array.shape[0])
        
            count_array: np.ndarray = np.expand_dims(np.array([255, np.count_nonzero(im_array[np.bool(mask_array)] > 0)]), 0)
            background_counts: int = np.count_nonzero(im_array[np.bool(mask_array)] == 0)
            
            if include_background:
                
                count_array = np.vstack((np.array([0, background_counts]), count_array))
            
        else:
            
            count_array: np.ndarray = np.expand_dims(np.array([255, np.count_nonzero(im_array > 0)]), 0)
            background_counts: int = np.count_nonzero(im_array == 0)
            
            if include_background:
                
                count_array = np.vstack((np.array([0, background_counts]), count_array))
        
    else:
        
        phase_array: np.ndarray = np.unique(im_array)
        
        if not include_background:
            
            phase_array = np.delete(phase_array, np.argwhere(phase_array == background))
        
        count_array: np.ndarray = np.empty(phase_array.shape)
        
        if np.any(mask_array):
            
            if mask_array.ndim < im_array.ndim:
                
                mask_array = cc.project_mask(mask_array, im_array.shape[0])
            
            background_counts: int = np.count_nonzero(im_array[np.bool(mask_array)] == 0)
            
        else:
            
            background_counts: int = np.count_nonzero(im_array == 0)
        
        for index, phase in enumerate(phase_array):
            
            if np.any(mask_array):
                
                count_array[index] = np.count_nonzero(im_array[np.bool(mask_array)] == phase)
            
            else:
            
                count_array[index] = np.count_nonzero(im_array == phase)
            
        count_array = np.stack((phase_array, count_array), 1)
        
    if normalize:
        
        if include_background:
        
            count_array[:, 1] = count_array[:, 1] / np.sum(count_array[:, 1])
            
        else:
            
            count_array[:, 1] = count_array[:, 1] / (np.sum(count_array[:, 1]) + background_counts)
    
    return count_array.T    
    
def get_volume(im_array: np.ndarray, *, mask_array: np.ndarray = None, scale: float = 1.0, units: str = "pix", include_background: bool = False, background: float | int = 0, normalize: bool = False) -> pd.DataFrame:
    
    if units == "um":
        
        units = "\u00b5m"
    
    count_array = __vol_area_precondition(im_array,
                                          mask_array = mask_array,
                                          include_background = include_background,
                                          background = background,
                                          normalize = normalize)
    
    if not normalize:
        
        count_array[1:, :] = count_array[1:, :] * (scale ** 3)
        
    vol_df: pd.DataFrame = pd.DataFrame(count_array[1:, :], columns = count_array[0, :])
    
    if not normalize:
        
        vol_df.attrs = {"units": f"{units}\u00b3"}
        
    else:
        
        vol_df.attrs = {"units": "dimensionless"}
    
    if normalize:
        
        for col in vol_df:
            
            current_str: str = str(col) + ":"
            print(f"\n{current_str:<16} {vol_df[col][0]}")
    
    else:
    
        for col in vol_df:
            
            current_str: str = str(col) + ":"
            print(f"\n{current_str:<16} {vol_df[col][0]} {vol_df.attrs["units"]}")
    
    return vol_df

def get_area(im_array: np.ndarray, *, mask_array: np.ndarray = None, scale: float = 1.0, units: str = "pix", include_background: bool = False, background: float | int = 0, normalize: bool = False) -> pd.DataFrame:
    
    if units == "um":
        
        units = "\u00b5m"
    
    count_array = __vol_area_precondition(im_array,
                                          mask_array = mask_array,
                                          include_background = include_background,
                                          background = background,
                                          normalize = normalize)
    
    if not normalize:
        
        count_array[1:, :] = count_array[1:, :] * (scale ** 2)
        
    area_df: pd.DataFrame = pd.DataFrame(count_array[1:, :], columns = count_array[0, :])
    
    if not normalize:
        
        area_df.attrs = {"units": f"{units}\u00b2"}
        
    else:
        
        area_df.attrs = {"units": "dimensionless"}
    
    if normalize:
        
        for col in area_df:
            
            current_str: str = str(col) + ":"
            print(f"\n{current_str:<16} {area_df[col][0]}")
    
    else:
    
        for col in area_df:
            
            current_str: str = str(col) + ":"
            print(f"\n{current_str:<16} {area_df[col][0]} {area_df.attrs["units"]}")
    
    return area_df

def get_contact(im_array: np.ndarray, phase_ints: tuple[int] | int | None = None, *,
                mask_array: np.ndarray = None,
                return_mode: str = "count") -> int:
    
    if phase_ints == None:
        
        max_array: np.ndarray = im_array == np.max(im_array)
        min_array: np.ndarray = im_array != np.max(im_array)
        
    elif not isinstance(phase_ints, tuple):
        
        max_array: np.ndarray = im_array == phase_ints
        min_array: np.ndarray = im_array != phase_ints
        
    else:
        
        max_array: np.ndarray = im_array == max(phase_ints)
        min_array: np.ndarray = im_array == min(phase_ints)
        
    if np.any(mask_array):
        
        if mask_array.ndim < im_array.ndim:
            
            mask_array = cc.project_mask(mask_array, im_array.shape[0])
        
        max_array[np.logical_not(mask_array)] = False
        min_array[np.logical_not(mask_array)] = False
        
    if return_mode == "array":
        
        contact_array: np.ndarray = np.zeros(im_array.shape, "uint8")
    
    if im_array.ndim == 3:
        
        zer_insert: np.ndarray = np.zeros((1, im_array.shape[1], im_array.shape[2]), np.bool)
        one_insert: np.ndarray = np.zeros((im_array.shape[0], 1, im_array.shape[2]), np.bool)
        two_insert: np.ndarray = np.zeros((im_array.shape[0], im_array.shape[1], 1), np.bool)
        offset_min_zer_beg: np.ndarray = np.delete(np.append(zer_insert, min_array, axis = 0), [-1], axis = 0)
        offset_min_zer_end: np.ndarray = np.delete(np.append(min_array, zer_insert, axis = 0), [0], axis = 0)
        offset_min_one_beg: np.ndarray = np.delete(np.append(one_insert, min_array, axis = 1), [-1], axis = 1)
        offset_min_one_end: np.ndarray = np.delete(np.append(min_array, one_insert, axis = 1), [0], axis = 1)
        offset_min_two_beg: np.ndarray = np.delete(np.append(two_insert, min_array, axis = 2), [-1], axis = 2)
        offset_min_two_end: np.ndarray = np.delete(np.append(min_array, two_insert, axis = 2), [0], axis = 2)
        contact_count: int = np.count_nonzero(max_array & offset_min_zer_beg)
        contact_count += np.count_nonzero(max_array & offset_min_zer_end)
        contact_count += np.count_nonzero(max_array & offset_min_one_beg)
        contact_count += np.count_nonzero(max_array & offset_min_one_end)
        contact_count += np.count_nonzero(max_array & offset_min_two_beg)
        contact_count += np.count_nonzero(max_array & offset_min_two_end)
        
        if return_mode == "array":
            
            contact_array[max_array & offset_min_zer_beg] = 255
            contact_array[max_array & offset_min_zer_end] = 255
            contact_array[max_array & offset_min_one_beg] = 255
            contact_array[max_array & offset_min_one_end] = 255
            contact_array[max_array & offset_min_two_beg] = 255
            contact_array[max_array & offset_min_two_end] = 255
    
    elif im_array.ndim == 2:
        
        zer_insert: np.ndarray = np.zeros((1, im_array.shape[1]), np.bool)
        one_insert: np.ndarray = np.zeros((im_array.shape[0], 1), np.bool)
        offset_min_zer_beg: np.ndarray = np.delete(np.append(zer_insert, min_array, axis = 0), [-1], axis = 0)
        offset_min_zer_end: np.ndarray = np.delete(np.append(min_array, zer_insert, axis = 0), [0], axis = 0)
        offset_min_one_beg: np.ndarray = np.delete(np.append(one_insert, min_array, axis = 1), [-1], axis = 1)
        offset_min_one_end: np.ndarray = np.delete(np.append(min_array, one_insert, axis = 1), [0], axis = 1)
        contact_count: int = np.count_nonzero(max_array & offset_min_zer_beg)
        contact_count += np.count_nonzero(max_array & offset_min_zer_end)
        contact_count += np.count_nonzero(max_array & offset_min_one_beg)
        contact_count += np.count_nonzero(max_array & offset_min_one_end)
        
        if return_mode == "array":
            
            contact_array[max_array & offset_min_zer_beg] = 255
            contact_array[max_array & offset_min_zer_end] = 255
            contact_array[max_array & offset_min_one_beg] = 255
            contact_array[max_array & offset_min_one_end] = 255
        
    if return_mode == "count":
        
        return contact_count
    
    elif return_mode == "array":
        
        return contact_array

def get_surface_contact(im_array: np.ndarray, phase_ints: tuple[int] | int | None = None, *,
                        pixel_size: float = 1.0,
                        units: str = "pix",
                        mask_array: np.ndarray = None) -> pd.DataFrame:
    
    if units == "um":
        
        units = "\u00b5m"
    
    contact_counts: int = get_contact(im_array, phase_ints, mask_array = mask_array)
    
    if phase_ints == None:
        
        phase_ints = (np.max(im_array))
        
    elif not isinstance(phase_ints, tuple):
        
        phase_ints = (phase_ints)
    
    if util.is_3d_rgb(im_array)["3D"]:
        
        if not isinstance(phase_ints, tuple):
            
            column_header: str = "Surface Area"
            
        else:
            
            column_header: str = "Contact Area"
        
        contact_df: pd.DataFrame = pd.DataFrame({"Gray Value": [str(phase_ints)], column_header: [contact_counts * (pixel_size ** 2)]})
        contact_df.attrs = {"units": f"{units}\u00b2"}
    
    else:
        
        if not isinstance(phase_ints, tuple):
            
            column_header: str = "Surface Perimeter"
            
        else:
            
            column_header: str = "Contact Perimeter"
        
        contact_df: pd.DataFrame = pd.DataFrame({"Gray Value": [str(phase_ints)], column_header: [contact_counts * pixel_size]})
        contact_df.attrs = {"units": units}
        
    print_str: str = str(contact_df.loc[0]["Gray Value"]) + ":"
    print(f"\n{print_str:<16} {contact_df.loc[0][column_header]} {contact_df.attrs["units"]}")
    
    return contact_df


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()