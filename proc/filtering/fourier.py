"""
Module for k-space filtering of images
"""


# Imports

import algotom.post.postprocessing as post
import numpy as np

from scipy import fft

import pixels
import util


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
        
def fft_ring_removal(im_array: np.ndarray, *,
                     cutoff_freq: int = 20,
                     filter_order: int = 8,
                     rows: int = 1,
                     sorting: bool = False,
                     square_axis: int = 0) -> np.ndarray:
    
    if util.check_if_square(im_array):
        
        if im_array.ndim == 2:
            
            return pixels.convert_im_type(post.remove_ring_based_fft(im_array, cutoff_freq, filter_order, rows, sorting), im_array.dtype)
        
        else:
            
            if square_axis != 0:
            
                proc_array: np.ndarray = util.get_along_axis_array(im_array, square_axis)
                rr_array: np.ndarray = np.empty(proc_array.shape)
            
                for n in range(0, proc_array.shape[0]):
                
                    rr_array[n] = post.remove_ring_based_fft(proc_array[n], cutoff_freq, filter_order, rows, sorting)
                
                return pixels.convert_im_type(util.undo_axial_array(rr_array, square_axis), im_array.dtype)
            
            else:
                
                rr_array: np.ndarray = np.empty(im_array.shape)
                
                for n in range(0, im_array.shape[0]):
                
                    rr_array[n] = post.remove_ring_based_fft(im_array[n], cutoff_freq, filter_order, rows, sorting)
                
                return pixels.convert_im_type(rr_array, im_array.dtype)
    
    else:
        
        print("Array not square!")
        
def wavelet_ring_removal(im_array: np.ndarray, *,
                         level: int = 5,
                         size: int = 1,
                         wavelet: str = "db9",
                         sorting: bool = False,
                         square_axis: int = 0) -> np.ndarray:
    
    if util.check_if_square(im_array):
        
        if im_array.ndim == 2:
            
            return pixels.convert_im_type(post.remove_ring_based_wavelet_fft(im_array, level, size, wavelet, sorting), im_array.dtype)
        
        else:
            
            if square_axis != 0:
            
                proc_array: np.ndarray = util.get_along_axis_array(im_array, square_axis)
                rr_array: np.ndarray = np.empty(proc_array.shape)
            
                for n in range(0, proc_array.shape[0]):
                
                    rr_array[n] = post.remove_ring_based_wavelet_fft(proc_array[n], level, size, wavelet, sorting)
                
                return pixels.convert_im_type(util.undo_axial_array(rr_array, square_axis), im_array.dtype)
            
            else:
                
                rr_array: np.ndarray = np.empty(im_array.shape)
                
                for n in range(0, im_array.shape[0]):
                
                    rr_array[n] = post.remove_ring_based_wavelet_fft(im_array[n], level, size, wavelet, sorting)
                
                return pixels.convert_im_type(rr_array, im_array.dtype)
    
    else:
        
        print("Array not square!")
    

# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()