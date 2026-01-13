"""
Module for analysis of segmented images
"""

# Imports

import numpy as np

from skimage import exposure


# Functions

def get_histogram(im_array: np.ndarray, *, mask_array: np.ndarray = None) -> dict[str, np.ndarray]:
    
    if np.any(mask_array):
    
        counts, bin_centers = exposure.histogram(im_array[mask_array])
        
    else:
        
        counts, bin_centers = exposure.histogram(im_array)
        
    return {"counts": counts, "bin centers": bin_centers}

def get_cdf(im_array: np.ndarray, *, mask_array: np.ndarray = None) -> dict[str, np.ndarray]:
    
    if np.any(mask_array):
    
        im_cdf, bin_centers = exposure.cumulative_distribution(im_array[mask_array])
        
    else:
        
        im_cdf, bin_centers = exposure.cumulative_distribution(im_array)
        
    return {"cdf": im_cdf, "bin centers": bin_centers}


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()