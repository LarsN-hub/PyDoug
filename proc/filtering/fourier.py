"""
Module for k-space filtering of images
"""

# Imports

import numpy as np

from scipy import fft


# Functions

def ft(im_array: np.ndarray) -> np.array:
    
    if len(im_array.shape) == 2:
        
        return fft.fftshift(fft.fft2(np.astype(im_array, np.float64)))
    
    else:
        
        return fft.fftshift(fft.fftn(np.astype(im_array, np.float64)))

def ift(im_array: np.ndarray) -> np.array:
    
    if len(im_array.shape) == 2:
        
        return fft.ifft2(fft.ifftshift(im_array))
    
    else:
        
        return fft.ifftn(fft.ifftshift(im_array))
    

# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()