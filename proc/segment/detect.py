"""
Module for detection-based image segmentation
"""

# Imports

import cropclip as cc
import numpy as np
import pixels
import quant

from scipy import ndimage as ndi
from skimage import segmentation
from skimage import filters
from skimage import feature
from segment import thresh


# Functions

def edge(im_array: np.ndarray, mask_array: np.ndarray = None, *, method: str = "sobel", sigma: float = 1.0, ksize: int = 3, alpha: float = 100, igg_sigma: float = 5, convert_type: bool = True) -> np.ndarray:
    
    if np.any(mask_array):
        
        if len(mask_array.shape) < len(im_array.shape):
            
            mask_array = cc.mask_2d_to_3d(mask_array, im_array.shape[0])
    
    if method == "sobel":
        
        edge_array: np.ndarray = filters.sobel(im_array, mask = mask_array)
    
    elif method == "canny":
        
        if len(im_array.shape) > 2:
        
            edge_array: np.ndarray = np.empty(im_array.shape)
            
            if np.any(mask_array):
            
                for slice_index in range(0, im_array.shape[0]):
            
                    edge_array[slice_index] = feature.canny(im_array[slice_index], sigma = sigma, mask = mask_array[slice_index], mode = "reflect")
                    
            else:
                
                for slice_index in range(0, im_array.shape[0]):
            
                    edge_array[slice_index] = feature.canny(im_array[slice_index], sigma = sigma, mode = "reflect")
                    
        else:
            
            edge_array = feature.canny(im_array, sigma = sigma, mask = mask_array, mode = "reflect")
    
    elif method == "farid":
        
        edge_array: np.ndarray = filters.farid(im_array, mask = mask_array)
        
    elif method == "IGG":
        
        if np.any(mask_array):
            
            edge_array: np.ndarray = segmentation.inverse_gaussian_gradient(cc.mask(im_array, mask_array), alpha, igg_sigma)
        
        else:
        
            edge_array: np.ndarray = segmentation.inverse_gaussian_gradient(im_array, alpha, igg_sigma)
    
    elif method == "laplace":
        
        edge_array: np.ndarray = filters.laplace(im_array, ksize = ksize, mask = mask_array)
    
    elif method == "prewitt":
        
        edge_array: np.ndarray = filters.prewitt(im_array, mask = mask_array)
    
    elif method == "roberts":
        
        if len(im_array.shape) > 2:
        
            edge_array: np.ndarray = np.empty(im_array.shape)
            
            if np.any(mask_array):
            
                for slice_index in range(0, im_array.shape[0]):
            
                    edge_array[slice_index] = filters.roberts(im_array[slice_index], mask = mask_array[slice_index])
                    
            else:
                
                for slice_index in range(0, im_array.shape[0]):
            
                    edge_array[slice_index] = filters.roberts(im_array[slice_index])
                    
        else:
            
            edge_array = filters.roberts(im_array, mask = mask_array)
    
    elif method == "scharr":
        
        edge_array: np.ndarray = filters.scharr(im_array, mask = mask_array)
    
    if convert_type:
        
        return pixels.convert_im_type(edge_array, im_array.dtype)
    
    else:
        
        return edge_array
    
def level_set(array_shape: tuple, method: str = "checkerboard", *, square_size: int = 5, radius: float = 10) -> np.ndarray:
    
    if method == "checkerboard":
        
        return segmentation.checkerboard_level_set(array_shape, square_size)
        
    elif method == "disk":
        
        return segmentation.disk_level_set(array_shape, radius = radius)
    
def morph_snakes(im_array: np.ndarray, method: str = "ACWE", *, init_levels_method: str = "checkerboard", square_size: int = 5, radius: float = 10, num_iter: int = 10, smoothing: int = 1, alpha: float = 100, sigma: float = 5) -> np.ndarray:
    
    init_levels: np.ndarray = level_set(im_array.shape, square_size = square_size, radius = radius)
    
    if method == "ACWE":
        
        morph_array: np.ndarray = segmentation.morphological_chan_vese(im_array, num_iter = num_iter, init_level_set = init_levels, smoothing = smoothing)
    
    elif method == "GAC":
        
        morph_array: np.ndarray = segmentation.morphological_chan_vese(edge(im_array, method = "IGG", alpha = alpha, sigma_2 = sigma, convert_type = False), num_iter = num_iter, init_level_set = init_levels, smoothing = smoothing)
        
    return pixels.convert_im_type(morph_array, "uint8", norm = True)

def random_walk(im_array: np.ndarray, marker_percentiles: tuple, beta: float = 130) -> np.ndarray:
    
    marker_ints: tuple = quant.get_percent_intensities(im_array, marker_percentiles)
    markers = np.zeros(im_array.shape, dtype = np.uint8)
    markers[im_array < min(marker_ints)] = 1
    markers[im_array > max(marker_ints)] = 2
    
    return pixels.normalize(segmentation.random_walker(im_array, markers, beta))

def watershed(im_array: np.ndarray, water_line: bool = False) -> np.ndarray:
    
    distance: np.ndarray = ndi.distance_transform_edt(im_array)
    peak_coords: np.ndarray = feature.peak_local_max(distance, footprint = np.ones((3, 3, 3)), labels = im_array)
    mask_array: np.ndarray = np.zeros(distance.shape, dtype = bool)
    mask_array[tuple(peak_coords.T)] = True
    markers: np.ndarray = thresh.label(mask_array)
    
    return segmentation.watershed(-distance, markers, mask = im_array)

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