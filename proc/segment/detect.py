"""
Module for detection-based image segmentation
"""

# Imports

import cropclip as cc
import numpy as np
import pixels

from skimage import segmentation
from skimage import filters
from skimage import feature


# Functions

def edge(im_array: np.ndarray, mask_array: np.ndarray = None, *, method: str = "sobel", sigma: float = 1.0, ksize: int = 3, alpha: float = 100, sigma_2: float = 5, convert_type: bool = True) -> np.ndarray:
    
    if np.any(mask_array):
        
        if len(mask_array.shape) < len(im_array.shape):
            
            mask_array = cc.mask_2d_to_3d(mask_array, im_array.shape[0])
    
    if method == "sobel":
        
        edge_array: np.ndarray = filters.sobel(im_array, mask = mask_array)
    
    elif method == "canny":
        
        edge_array: np.ndarray = np.empty(im_array.shape)
        
        if np.any(mask_array):
        
            for slice_index in range(0, im_array.shape[0]):
        
                edge_array[slice_index] = feature.canny(im_array[slice_index], sigma = sigma, mask = mask_array[slice_index], mode = "reflect")
                
        else:
            
            for slice_index in range(0, im_array.shape[0]):
        
                edge_array[slice_index] = feature.canny(im_array[slice_index], sigma = sigma, mode = "reflect")
    
    elif method == "farid":
        
        edge_array: np.ndarray = filters.farid(im_array, mask = mask_array)
        
    elif method == "igg":
        
        if np.any(mask_array):
            
            pass
        
        else:
        
            edge_array: np.ndarray = segmentation.inverse_gaussian_gradient(im_array, alpha, sigma_2)
    
    elif method == "laplace":
        
        edge_array: np.ndarray = filters.laplace(im_array, ksize = ksize, mask = mask_array)
    
    elif method == "prewitt":
        
        edge_array: np.ndarray = filters.prewitt(im_array, mask = mask_array)
    
    elif method == "roberts":
        
        edge_array: np.ndarray = np.empty(im_array.shape)
        
        if np.any(mask_array):
        
            for slice_index in range(0, im_array.shape[0]):
        
                edge_array[slice_index] = filters.roberts(im_array[slice_index], mask = mask_array[slice_index])
                
        else:
            
            for slice_index in range(0, im_array.shape[0]):
        
                edge_array[slice_index] = filters.roberts(im_array[slice_index])
    
    elif method == "scharr":
        
        edge_array: np.ndarray = filters.scharr(im_array, mask = mask_array)
    
    if convert_type:
        
        return pixels.convert_im_type(edge_array, im_array.dtype)
    
    else:
        
        return edge_array
    
def morph_snakes(im_array: np.ndarray, method: str = "ACWE") -> np.ndarray:
    
    pass

def active_contour(im_array: np.ndarray, method: str = "ACWE") -> np.ndarray:
    
    pass

def random_walk(im_array: np.ndarray) -> np.ndarray:
    
    pass

def watershed(im_array: np.ndarray) -> np.ndarray:
    
    pass

def corners(im_array: np.ndarray) -> np.ndarray:
    
    pass


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()