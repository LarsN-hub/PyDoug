"""
Module for obtaining distributions of image data
"""

# Imports

import cropclip as cc
import pandas as pd
import numpy as np
import quant

from skimage import exposure
from segment import thresh


# Functions

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

def get_position_distribution(im_array: np.ndarray, *, mask_array: np.ndarray = None, mode: str = "vol", scale: float = 1.0, units: str = "pix", temporal_scale: float | int = None, temporal_units: str = "s", axis: int = 0, include_background: bool = False, background: float | int = 0) -> pd.DataFrame:
    
    if temporal_scale:
        
        pos_scale = temporal_scale
        pos_units = temporal_units
        
    else:
        
        pos_scale = scale
        pos_units = units
    
    phases: np.ndarray = np.unique(im_array)
    
    if not include_background:
        
        phases = np.delete(phases, np.argwhere(phases == background))
        
    pos_array: np.ndarray = np.zeros((im_array.shape[axis], 1 + len(phases)))
    
    for slice_index in range(0, im_array.shape[axis]):
        
        pos_array[slice_index, 0] = slice_index * pos_scale
    
        if axis == 0:
            
            int_im_array: np.ndarray = im_array[slice_index]
            
            if np.any(mask_array):
                
                int_mask_array: np.ndarray = mask_array[slice_index]
                
            else:
                
                int_mask_array = None
            
        elif axis == 1:
            
            int_im_array: np.ndarray = im_array[:, slice_index, :]
            
            if np.any(mask_array):
                
                int_mask_array: np.ndarray = mask_array[:, slice_index, :]
                
            else:
                
                int_mask_array = None
        
        elif axis == 2:

            int_im_array: np.ndarray = im_array[:, :, slice_index]
            
            if np.any(mask_array):
                
                int_mask_array: np.ndarray = mask_array[:, :, slice_index]
                
            else:
                
                int_mask_array = None
            
        int_array: np.ndarray = quant.__vol_area_precondition(int_im_array, mask_array = int_mask_array, include_background = include_background, background = background)
        
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

def __get_size_distribution(im_array: np.ndarray, *, mask_array: np.ndarray = None, mode: str = "vol", scale: float = 1.0, units: str = "pix", background: float | int = 0) -> pd.DataFrame:
    
    if np.any(mask_array):
        
        counts, labels = exposure.histogram(im_array[mask_array])
        counts = np.delete(counts, np.argwhere(counts == 0))
        
    else:
        
        counts, labels = exposure.histogram(im_array)
        
    counts = np.delete(counts, np.argwhere(labels == background))
    
    if len(counts) != 0:
        
        size_counts, sizes = exposure.histogram(counts)
        
    else:
        
        size_counts: np.ndarray = np.array([0, 0])
        sizes: np.ndarray = np.array([1, 2])
    
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

def get_size_distribution(im_array: np.ndarray, *, mask_array: np.ndarray = None, mode: str = "vol", scale: float = 1.0, units: str = "pix", connectivity: int = None, background: float | int = 0, positional: bool = False, temporal_scale: float | int = None, temporal_units: str = "s") -> pd.DataFrame:
    
    if np.any(mask_array):
        
        if mask_array.ndim < im_array.ndim:
            
            mask_array = cc.project_mask(mask_array, im_array.shape[0])
    
    if not positional:
    
        if im_array.dtype != np.int64:
            
            lab_array = thresh.label(im_array, connectivity = connectivity, background = background)
            size_df: pd.DataFrame = __get_size_distribution(lab_array, mask_array = mask_array, mode = mode, scale = scale, units = units, background = background)
            
        else:
            
            size_df: pd.DataFrame = __get_size_distribution(im_array, mask_array = mask_array, mode = mode, scale = scale, units = units, background = background)
            
        return size_df
    
    else:
        
        if temporal_scale:
            
            pos_scale = temporal_scale
            pos_units = temporal_units
            
        else:
            
            pos_scale = scale
            pos_units = units
            
        if im_array.dtype != np.int64:
            
            lab_array = thresh.label(im_array, connectivity = connectivity, background = background, positional = True)
            
        if mode == "vol":
            
            size_interval: float | int = scale ** 3
            
        elif mode == "area":
            
            size_interval: float | int = scale ** 2
            
        columns = ["Size"]
            
        for slice_index in range(0, im_array.shape[0]):
            
            if im_array.dtype != np.int64:
                
                int_im_array = lab_array[slice_index]
                
            else:
                
                int_im_array = im_array[slice_index]
            
            if np.any(mask_array):
                
                int_df: pd.DataFrame = __get_size_distribution(int_im_array, mask_array = mask_array[slice_index], mode = mode, scale = scale, units = units, background = background)
            
            else:
                
                int_df: pd.DataFrame = __get_size_distribution(int_im_array, mode = mode, scale = scale, units = units, background = background)
                
            columns.append(str(pos_scale * slice_index))
            int_sizes: np.ndarray = np.squeeze(np.array([int_df["Bin Centers"]]))
            int_counts: np.ndarray = np.squeeze(np.array([int_df["Counts"]]))
            
            if not int_sizes.shape:
                
                int_sizes = np.expand_dims(int_sizes, 0)
                int_counts = np.expand_dims(int_counts, 0)
            
            if slice_index == 0:
                
                size_array: np.ndarray = np.arange(size_interval, (np.max(int_sizes) + size_interval), size_interval)
                size_array = np.expand_dims(size_array, 1)
                
            if size_array[0, 0] != int_sizes[0]:
                
                insert_array: np.ndarray = np.arange(size_interval, int_sizes[0], size_interval)
                insert_zeros: np.ndarray = np.zeros(insert_array.shape)
                int_sizes = np.append(insert_array, int_sizes)
                int_counts = np.append(insert_zeros, int_counts)
            
            if size_array[-1, 0] > int_sizes[-1]:
                
                append_array: np.ndarray = np.arange((int_sizes[-1] + size_interval), size_array[-1, 0] + size_interval, size_interval)
                append_zeros: np.ndarray = np.zeros(append_array.shape)
                int_sizes = np.append(int_sizes, append_array)
                int_counts = np.append(int_counts, append_zeros)
            
            elif size_array[-1, 0] < int_sizes[-1]:
                
                stack_array: np.ndarray = np.expand_dims(np.arange((size_array[-1, 0] + size_interval), int_sizes[-1] + size_interval, size_interval), 0)
                stack_zeros: np.ndarray = np.zeros(((size_array.shape[1] - 1), stack_array.shape[1]))
                stack_array = np.vstack((stack_array, stack_zeros)).T
                size_array = np.vstack((size_array, stack_array))
                
            size_array = np.hstack((size_array, np.expand_dims(int_counts, 1)))
            
        size_df: pd.DataFrame = pd.DataFrame(size_array, columns = columns)
        
        if mode == "vol":
            
            if temporal_scale:
                
                size_df.attrs = {"time_units": f"{pos_units}", "vol_units": f"{units}^3"}
                
            else:
                
                size_df.attrs = {"pos_units": f"{pos_units}", "vol_units": f"{units}^3"}
            
        elif mode == "area":

            if temporal_scale:
                
                size_df.attrs = {"time_units": f"{pos_units}", "area_units": f"{units}^2"}
                
            else:
                
                size_df.attrs = {"pos_units": f"{pos_units}", "area_units": f"{units}^2"}
            
        return size_df

def get_time_series(im_array: np.ndarray, mode: str = "vol", *, mask_array: np.ndarray = None, size_mode: str = "area", scale: float | int = 1.0, spatial_units: str = "pix", temporal_units: str = "s", temporal_scale: float | int = 1.0, connectivity: int = None, axis: int = 0, include_background: bool = False, background: float | int = 0) -> pd.DataFrame:
    
    if mode == "size":
        
        time_df: pd.DataFrame = get_size_distribution(im_array, mask_array = mask_array, mode = size_mode, scale = scale, units = spatial_units, connectivity = connectivity, background = background, positional = True, temporal_scale = temporal_scale, temporal_units = temporal_units)
    
    elif mode == "vol":
        
        time_df: pd.DataFrame = get_position_distribution(im_array, mode = mode, mask_array = mask_array, scale = scale, units = spatial_units, temporal_units = temporal_units, temporal_scale = temporal_scale, axis = axis, include_background = include_background, background = background)

    elif mode == "area":
        
        time_df: pd.DataFrame = get_position_distribution(im_array, mode = mode, mask_array = mask_array, scale = scale, units = spatial_units, temporal_units = temporal_units, temporal_scale = temporal_scale, axis = axis, include_background = include_background, background = background)
    
    return time_df