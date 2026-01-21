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

def edge(im_array: np.ndarray, mask_array: np.ndarray = None, *, method: str = "sobel", sigma: float = 1.0, ksize: int = 3) -> np.ndarray:
    
    if np.any(mask_array):
        
        if len(mask_array.shape) < len(im_array.shape):
            
            mask_array = cc.mask_2d_to_3d(mask_array, im_array.shape[0])
    
    if method == "sobel":
        
        return pixels.convert_im_type(filters.sobel(im_array, mask = mask_array), im_array.dtype)
    
    elif method == "canny":
        
        edge_array: np.ndarray = np.empty(im_array.shape)
        
        if np.any(mask_array):
        
            for slice_index in range(0, im_array.shape[0]):
        
                edge_array[slice_index] = feature.canny(im_array[slice_index], sigma = sigma, mask = mask_array[slice_index], mode = "reflect")
                
        else:
            
            for slice_index in range(0, im_array.shape[0]):
        
                edge_array[slice_index] = feature.canny(im_array[slice_index], sigma = sigma, mode = "reflect")
            
        return pixels.convert_im_type(edge_array, im_array.dtype)
    
    elif method == "farid":
        
        return pixels.convert_im_type(filters.farid(im_array, mask = mask_array), im_array.dtype)
    
    elif method == "laplace":
        
        return pixels.convert_im_type(filters.laplace(im_array, ksize = ksize, mask = mask_array), im_array.dtype)
    
    elif method == "prewitt":
        
        return pixels.convert_im_type(filters.prewitt(im_array, mask = mask_array), im_array.dtype)
    
    elif method == "roberts":
        
        edge_array: np.ndarray = np.empty(im_array.shape)
        
        if np.any(mask_array):
        
            for slice_index in range(0, im_array.shape[0]):
        
                edge_array[slice_index] = filters.roberts(im_array[slice_index], mask = mask_array[slice_index])
                
        else:
            
            for slice_index in range(0, im_array.shape[0]):
        
                edge_array[slice_index] = filters.roberts(im_array[slice_index])
            
        return pixels.convert_im_type(edge_array, im_array.dtype)
    
    elif method == "scharr":
        
        return pixels.convert_im_type(filters.scharr(im_array, mask = mask_array), im_array.dtype)
    
def region(im_array: np.ndarray) -> np.ndarray:
    
    pass

def watershed(seg_array: np.ndarray, *, markers = None, connectivity = 1) -> np.ndarray:
    
    return segmentation.watershed(seg_array, markers = markers, connectivity = connectivity)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()