"""
Module for filtering images
"""

# Imports

import numpy as np
import pixels

from skimage import restoration
from skimage import filters
from scipy import fft


# Functions

def bilateral(im_array: np.array, *,
              win_size: int | None = None,
              sigma_color: float | None = None,
              sigma_spatial: float = 1,
              bins: int = 10000,
              mode: str = "constant",
              cval: int | float = 0,
              channel_axis: int | None = None) -> np.array:
    
    bilat_array: np.array = np.empty(im_array.shape)
    
    for n in range(0, im_array.shape[0]):
            
        bilat_array[n] = restoration.denoise_bilateral(im_array[n], win_size, sigma_color, sigma_spatial, bins, mode, cval,
                                                       channel_axis = channel_axis)
        
    return pixels.convert_im_type(bilat_array, im_array.dtype)

def gaussian(im_array: np.array, *,
             sigma: float = 1,
             mode: str = "nearest",
             cval: int | float = 0,
             preserve_range: bool = False,
             truncate: float = 4,
             channel_axis: int | None = None,
             out: np.array | None = None) -> np.array:
    
    gaus_array: np.array = filters.gaussian(im_array, sigma,
                                            mode = mode,
                                            cval = cval,
                                            preserve_range = preserve_range,
                                            truncate = truncate,
                                            channel_axis = channel_axis,
                                            out = out)
    
    return pixels.convert_im_type(gaus_array, im_array.dtype)

def non_local_means(im_array: np.array, *,
                    patch_size: int = 7,
                    patch_distance: int = 11,
                    h: float = 0.1,
                    fast_mode: bool = True,
                    sigma: float = 0,
                    preserve_range: bool = False,
                    channel_axis: int | None = None) -> np.array:
    
    nl_array: np.array =  restoration.denoise_nl_means(im_array, patch_size, patch_distance, h, fast_mode, sigma,
                                                       preserve_range = preserve_range,
                                                       channel_axis = channel_axis)
    
    return pixels.convert_im_type(nl_array, im_array.dtype)

def tv_bregman(im_array: np.array, *,
               weight: float = 5,
               max_num_iter: int = 100,
               eps: float = 0.001,
               isotropic: bool = True,
               channel_axis: int | None = None) -> np.array:
    
    tv_array: np.array = restoration.denoise_tv_bregman(im_array, weight, max_num_iter, eps, isotropic,
                                                        channel_axis = channel_axis)
    
    return pixels.convert_im_type(tv_array, im_array.dtype)

def tv_chambolle(im_array: np.array, *,
                 weight: float = 0.1,
                 eps: float = 0.0002,
                 max_num_iter: int = 200,
                 channel_axis: int | None = None) -> np.array:
    
    tv_array: np.array = restoration.denoise_tv_chambolle(im_array, weight, eps, max_num_iter,
                                                          channel_axis = channel_axis)
    
    return pixels.convert_im_type(tv_array, im_array.dtype)

def wavelet(im_array: np.array, *,
            sigma: float | int = None,
            wavelet: str = "db1",
            mode: str = "soft",
            wavelet_levels: int | None = None,
            convert2ycbcr: bool = False,
            method: str = "BayesShrink",
            rescale_sigma: bool = True,
            channel_axis: int | None = None) -> np.array:
    
    wave_array: np.array = restoration.denoise_wavelet(im_array, sigma, wavelet, mode, wavelet_levels, convert2ycbcr, method, rescale_sigma,
                                                       channel_axis = channel_axis)
    
    return pixels.convert_im_type(wave_array, im_array.dtype)

def ft(im_array: np.array) -> np.array:
    
    if len(im_array.shape) == 2:
        
        return fft.fftshift(fft.fft2(np.astype(im_array, np.float64)))
    
    else:
        
        return fft.fftshift(fft.fftn(np.astype(im_array, np.float64)))

def ift(im_array: np.array) -> np.array:
    
    if len(im_array.shape) == 2:
        
        return fft.ifft2(fft.ifftshift(im_array))
    
    else:
        
        return fft.ifftn(fft.ifftshift(im_array))


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()