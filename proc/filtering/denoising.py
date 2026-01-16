"""
Module for denoising images
"""

# Imports

import numpy as np
import pixels
import typing

from skimage import restoration
from skimage import filters


# Functions

def bilateral(im_array: np.ndarray, *,
              win_size: int | None = None,
              sigma_color: float | None = None,
              sigma_spatial: float = 1,
              bins: int = 10000,
              mode: str = "constant",
              cval: int | float = 0,
              channel_axis: int | None = None) -> np.ndarray:
    
    bilat_array: np.ndarray = np.empty(im_array.shape)
    
    for n in range(0, im_array.shape[0]):
            
        bilat_array[n] = restoration.denoise_bilateral(im_array[n], win_size, sigma_color, sigma_spatial, bins, mode, cval,
                                                       channel_axis = channel_axis)
        
    return pixels.convert_im_type(bilat_array, im_array.dtype)

def gaussian(im_array: np.ndarray, *,
             sigma: float = 1,
             mode: str = "nearest",
             cval: int | float = 0,
             preserve_range: bool = False,
             truncate: float = 4,
             channel_axis: int | None = None,
             out: np.ndarray | None = None) -> np.ndarray:
    
    gaus_array: np.ndarray = filters.gaussian(im_array, sigma,
                                              mode = mode,
                                              cval = cval,
                                              preserve_range = preserve_range,
                                              truncate = truncate,
                                              channel_axis = channel_axis,
                                              out = out)
    
    return pixels.convert_im_type(gaus_array, im_array.dtype)

def median(im_array: np.ndarray, *,
           footprint: np.ndarray = None,
           out: np.ndarray = None,
           mask: np.ndarray = None,
           shift_x: int = 0,
           shift_y: int = 0,
           shift_z: int = 0) -> np.ndarray:
    
    return filters.rank.median(im_array, footprint, out, mask, shift_x, shift_y, shift_z)

def non_local_means(im_array: np.ndarray, *,
                    patch_size: int = 7,
                    patch_distance: int = 11,
                    h: float = 0.1,
                    fast_mode: bool = True,
                    sigma: float = 0,
                    preserve_range: bool = False,
                    channel_axis: int | None = None) -> np.ndarray:
    
    nl_array: np.ndarray =  restoration.denoise_nl_means(im_array, patch_size, patch_distance, h, fast_mode, sigma,
                                                         preserve_range = preserve_range,
                                                         channel_axis = channel_axis)
    
    return pixels.convert_im_type(nl_array, im_array.dtype)

def tv_bregman(im_array: np.ndarray, *,
               weight: float = 5,
               max_num_iter: int = 100,
               eps: float = 0.001,
               isotropic: bool = True,
               channel_axis: int | None = None) -> np.ndarray:
    
    tv_array: np.ndarray = restoration.denoise_tv_bregman(im_array, weight, max_num_iter, eps, isotropic,
                                                          channel_axis = channel_axis)
    
    return pixels.convert_im_type(tv_array, im_array.dtype)

def remove_background(im_array: np.ndarray, *,
                      radius: int = 100,
                      kernel: np.ndarray = None,
                      return_background: bool = False) -> np.ndarray:
    
    back_array: np.ndarray = restoration.rolling_ball(im_array,
                                                      radius = radius,
                                                      kernel = kernel)
    
    if return_background:
        
        return back_array
    
    else:
        
        return im_array - back_array

def tv_chambolle(im_array: np.ndarray, *,
                 weight: float = 0.1,
                 eps: float = 0.0002,
                 max_num_iter: int = 200,
                 channel_axis: int | None = None) -> np.ndarray:
    
    tv_array: np.ndarray = restoration.denoise_tv_chambolle(im_array, weight, eps, max_num_iter,
                                                            channel_axis = channel_axis)
    
    return pixels.convert_im_type(tv_array, im_array.dtype)

def wavelet(im_array: np.ndarray, *,
            sigma: float | int = None,
            wavelet: str = "db1",
            mode: str = "soft",
            wavelet_levels: int | None = None,
            convert2ycbcr: bool = False,
            method: str = "BayesShrink",
            rescale_sigma: bool = True,
            channel_axis: int | None = None) -> np.ndarray:
    
    wave_array: np.ndarray = restoration.denoise_wavelet(im_array, sigma, wavelet, mode, wavelet_levels, convert2ycbcr, method, rescale_sigma,
                                                         channel_axis = channel_axis)
    
    return pixels.convert_im_type(wave_array, im_array.dtype)

def calibrated_denoiser(im_array: np.ndarray, *,
                        denoiser: str,
                        parameters: dict[list],
                        stride: int = 4,
                        approximate_loss: bool = True,
                        extra_output: bool = False) -> None:
    
    pass


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()