"""
Module for k-space filtering of images
"""

# Imports

import numpy as np

from scipy import fft


# Functions

def ft(im_array: np.ndarray, along_axis: bool = False) -> np.array:
    
    if im_array.ndim == 2:
        
        return fft.fftshift(fft.fft2(np.astype(im_array, np.float64)))
    
    else:
        
        if along_axis:
            
            fft_array: np.ndarray = np.empty(im_array.shape)
            
            for slice_index in range(0, im_array.shape[0]):
                
                fft_array[slice_index] = fft.fftshift(fft.fft2(np.astype(im_array[slice_index], np.float64)))
                
            return fft_array
        
        else:
            
            return fft.fftshift(fft.fftn(np.astype(im_array, np.float64)))

def ift(im_array: np.ndarray, along_axis: bool = False) -> np.array:
    
    if im_array.ndim == 2:
        
        return fft.ifft2(fft.ifftshift(im_array))
    
    else:
        
        if along_axis:
            
            ifft_array: np.ndarray = np.empty(im_array.shape)
            
            for slice_index in range(0, im_array.shape[0]):
                
                ifft_array[slice_index] = fft.ifft2(fft.ifftshift(im_array[slice_index]))
        
        else:
        
            return fft.ifftn(fft.ifftshift(im_array))
    

# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()