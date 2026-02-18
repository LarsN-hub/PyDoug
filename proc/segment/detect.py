"""
Module for detection-based image segmentation
"""


# Imports

import numpy as np

from scipy import ndimage as ndi
from skimage import segmentation
from skimage import filters
from skimage import feature

import cropclip as cc
import pixels
import quant
import util

from segment import thresh


# Functions

def edge(im_array: np.ndarray, mask_array: np.ndarray = None, *, method: str = "sobel", sigma: float = 1.0, ksize: int = 3, alpha: float = 100, igg_sigma: float = 5, convert_type: bool = True, axis: int = None) -> np.ndarray:
    
    if np.any(mask_array):
        
        if mask_array.ndim < im_array.ndim:
            
            mask_array = cc.mask_2d_to_3d(mask_array, im_array.shape[0])
    
    if method == "sobel":
        
        edge_array: np.ndarray = filters.sobel(im_array, mask = mask_array, axis = axis)
    
    elif method == "canny":
        
        if len(im_array.shape) > 2:
        
            edge_array: np.ndarray = np.empty(im_array.shape)
            
            if np.any(mask_array):
            
                for slice_index in range(0, im_array.shape[0]):
            
                    edge_array[slice_index] = feature.canny(im_array[slice_index], sigma = sigma, mask = np.bool(mask_array[slice_index]), mode = "reflect")
                    
            else:
                
                for slice_index in range(0, im_array.shape[0]):
            
                    edge_array[slice_index] = feature.canny(im_array[slice_index], sigma = sigma, mode = "reflect")
                    
        else:
            
            edge_array = feature.canny(im_array, sigma = sigma, mask = mask_array, mode = "reflect")
    
    elif method == "farid":
        
        edge_array: np.ndarray = filters.farid(im_array, mask = mask_array, axis = axis)
        
    elif method == "igg":
        
        if np.any(mask_array):
            
            edge_array: np.ndarray = segmentation.inverse_gaussian_gradient(cc.mask(im_array, np.bool(mask_array)), alpha, igg_sigma)
        
        else:
        
            edge_array: np.ndarray = segmentation.inverse_gaussian_gradient(im_array, alpha, igg_sigma)
    
    elif method == "laplace":
        
        edge_array: np.ndarray = filters.laplace(im_array, ksize = ksize, mask = mask_array)
    
    elif method == "prewitt":
        
        edge_array: np.ndarray = filters.prewitt(im_array, mask = mask_array, axis = axis)
    
    elif method == "roberts":
        
        if len(im_array.shape) > 2:
        
            edge_array: np.ndarray = np.empty(im_array.shape)
            
            if np.any(mask_array):
            
                for slice_index in range(0, im_array.shape[0]):
            
                    edge_array[slice_index] = filters.roberts(im_array[slice_index], mask = np.bool(mask_array[slice_index]))
                    
            else:
                
                for slice_index in range(0, im_array.shape[0]):
            
                    edge_array[slice_index] = filters.roberts(im_array[slice_index])
                    
        else:
            
            edge_array = filters.roberts(im_array, mask = mask_array)
    
    elif method == "scharr":
        
        edge_array: np.ndarray = filters.scharr(im_array, mask = mask_array, axis = axis)
    
    if convert_type:
        
        return pixels.convert_im_type(edge_array, im_array.dtype)
    
    else:
        
        return edge_array
    
def level_set(array_shape: tuple, method: str = "checkerboard", *, square_size: int = 5, radius: float = 10) -> np.ndarray:
    
    if method == "checkerboard":
        
        return segmentation.checkerboard_level_set(array_shape, square_size)
        
    elif method == "disk":
        
        return segmentation.disk_level_set(array_shape, radius = radius)
    
def morph_snakes(im_array: np.ndarray, method: str = "ACWE", *, square_size: int = 5, radius: float = 10, num_iter: int = 10, smoothing: int = 1, alpha: float = 100, sigma: float = 5) -> np.ndarray:
    
    init_levels: np.ndarray = level_set(im_array.shape, square_size = square_size, radius = radius)
    
    if method == "ACWE":
        
        morph_array: np.ndarray = segmentation.morphological_chan_vese(im_array, num_iter = num_iter, init_level_set = init_levels, smoothing = smoothing)
    
    elif method == "GAC":
        
        morph_array: np.ndarray = segmentation.morphological_chan_vese(edge(im_array, method = "igg", alpha = alpha, sigma_2 = sigma, convert_type = False), num_iter = num_iter, init_level_set = init_levels, smoothing = smoothing)
        
    return pixels.convert_im_type(morph_array, "uint8", norm = True)

def random_walk(im_array: np.ndarray, marker_percentiles: tuple, beta: float = 130) -> np.ndarray:
    
    marker_ints: tuple = quant.get_percent_intensities(im_array, marker_percentiles)
    markers = np.zeros(im_array.shape, dtype = np.uint8)
    markers[im_array < min(marker_ints)] = 1
    markers[im_array > max(marker_ints)] = 2
    
    return pixels.normalize(segmentation.random_walker(im_array, markers, beta))

def watershed(im_array: np.ndarray, *, background: float | int = 0, mask_array: np.ndarray = None, water_line: bool = False, connectivity: int = 2, compactness: float = 0, along_axis: bool = False, axis: int = 0, randomize: bool = True) -> np.ndarray:
    
    if np.any(mask_array):
        
        if mask_array.ndim < im_array.ndim:
            
            mask_array = cc.project_mask(mask_array, im_array.shape[0])
            
        im_array[np.logical_not(np.bool(mask_array))] = background
        
    if im_array.dtype != np.bool:
        
        proc_array = np.bool(im_array)
        
    if im_array.ndim == 2:
        
        distance: np.ndarray = ndi.distance_transform_edt(proc_array)
        peak_coords: np.ndarray = feature.peak_local_max(distance, footprint = np.ones((3, 3)), labels = proc_array)
        water_mask_array: np.ndarray = np.zeros(distance.shape, dtype = bool)
        water_mask_array[tuple(peak_coords.T)] = True
        markers: np.ndarray = thresh.label(water_mask_array)
        water_array: np.ndarray = segmentation.watershed(-distance, markers, connectivity = connectivity, compactness = compactness, mask = proc_array)
    
    elif along_axis:
        
        proc_array: np.ndarray = util.get_along_axis_array(proc_array, axis)
        water_array: np.ndarray = np.empty(proc_array.shape)
        
        for slice_index in range(0, proc_array.shape[0]):
            
            int_im_array: np.ndarray = proc_array[slice_index]
            distance: np.ndarray = ndi.distance_transform_edt(int_im_array)
            peak_coords: np.ndarray = feature.peak_local_max(distance, footprint = np.ones((3, 3)), labels = int_im_array)
            water_mask_array: np.ndarray = np.zeros(distance.shape, dtype = bool)
            water_mask_array[tuple(peak_coords.T)] = True
            markers: np.ndarray = thresh.label(water_mask_array)
            water_array[slice_index] = segmentation.watershed(-distance, markers, connectivity = connectivity, compactness = compactness, mask = int_im_array)
            
        water_array = util.undo_axial_array(water_array, axis)
    
    else:
        
        distance: np.ndarray = ndi.distance_transform_edt(proc_array)
        peak_coords: np.ndarray = feature.peak_local_max(distance, footprint = np.ones((3, 3, 3)), labels = proc_array)
        water_mask_array: np.ndarray = np.zeros(distance.shape, dtype = bool)
        water_mask_array[tuple(peak_coords.T)] = True
        markers: np.ndarray = thresh.label(water_mask_array)
        water_array: np.ndarray = segmentation.watershed(-distance, markers, connectivity = connectivity, compactness = compactness, mask = proc_array)
    
    if randomize:
        
        return thresh.randomize_labels(water_array)
    
    else:
        
        return water_array

def corners(im_array: np.ndarray, method = "fast", *, n: int = 12, threshold: float = 0.15, harris_method: str = "k", k: int = 0.05, eps: int = 0.000001, sigma: float = 1, window_size: int = 1, return_mode: str = "coords") -> np.ndarray:
    
    corner_array: np.ndarray = np.empty(im_array.shape)
    
    if method == "fast":
        
        if len(im_array.shape) > 2:
        
            for slice_index in range(0, im_array.shape[0]):
            
                corner_array[slice_index] = feature.corner_fast(im_array[slice_index], n, threshold)
                
        else:
            
            corner_array = feature.corner_fast(im_array, n, threshold)
    
    elif method == "harris":
        
        if len(im_array.shape) > 2:
        
            for slice_index in range(0, im_array.shape[0]):
            
                corner_array[slice_index] = feature.corner_harris(im_array[slice_index], harris_method, k, eps, sigma)
                
        else:
            
            corner_array = feature.corner_harris(im_array, harris_method, k, eps, sigma)
        
    elif method == "kitchen rosenfeld":
        
        if len(im_array.shape) > 2:
        
            for slice_index in range(0, im_array.shape[0]):
            
                corner_array[slice_index] = feature.corner_kitchen_rosenfeld(im_array[slice_index], "reflect")
                
        else:
            
            corner_array = feature.corner_kitchen_rosenfeld(im_array, "reflect")
    
    elif method == "moravec":
        
        if len(im_array.shape) > 2:
        
            for slice_index in range(0, im_array.shape[0]):
            
                corner_array[slice_index] = feature.corner_moravec(im_array[slice_index], window_size)
                
        else:
            
            corner_array = feature.corner_moravec(im_array, window_size)
    
    elif method == "shi tomasi":
        
        if len(im_array.shape) > 2:
        
            for slice_index in range(0, im_array.shape[0]):
            
                corner_array[slice_index] = feature.corner_shi_tomasi(im_array[slice_index], sigma)
                
        else:
            
            corner_array = feature.corner_shi_tomasi(im_array, sigma)
        
    if return_mode == "coords":
        
        return feature.corner_peaks(corner_array)
    
    elif return_mode == "array":
        
        return feature.corner_peaks(corner_array, indices = False)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()