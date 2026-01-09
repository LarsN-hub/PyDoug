"""
Module for smoothing, denoising, and ffts of images
"""

# Imports

import numpy as np
import pixels

from skimage import restoration
from skimage import filters
from scipy import fft


# Classes

class Parameters:
    
    def __init__(self, filter_type: str) -> None:
        
        self.filter_type = filter_type
        
        if filter_type == "gaussian":
            
            self.sigma: float = 1
            self.mode: str = "nearest"
            self.cval: float = 0
            self.preserve_range: bool = False
            self.truncate: float = 4
            self.channel_axis: int = None
            self.out = None
            
        elif filter_type == "bilateral":
            
            self.win_size: int = 5
            self.sigma_color: float = None
            self.sigma_spatial: float = 1
            self.bins: float = 10000
            self.mode: str = "constant"
            self.cval: float = 0
            self.channel_axis: int = None
            
        elif filter_type == "non-local means":
            
            self.patch_size: int = 7
            self.patch_distance: int = 11
            self.h: float = 0.1
            self.fast_mode: bool = True
            self.sigma: float = 0
            self.preserve_range: bool = False
            self.channel_axis: int = None
            
        elif filter_type == "tv bregman":
            
            self.weight: float = 5
            self.max_num_iter: int = 100
            self.eps: float = 0.001
            self.isotropic: bool = True
            self.channel_axis: int = None
            
        elif filter_type == "tv chambolle":
            
            self.weight: float = 0.1
            self.eps: float = 0.0002
            self.max_num_iter: int = 200
            self.channel_axis: int = None
            
        elif filter_type == "wavelet":
            
            self.sigma: float = None
            self.wavelet: str = "db1"
            self.mode: str = "soft"
            self.wavelet_levels: int = None
            self.convert2ycbcr: bool = False
            self.method: str = "BayesShrink"
            self.rescale_sigma: bool = True
            self.channel_axis: int = None
            
        else:
            
            print("\nInvalid filter type!")


# Functions

def denoise(im_array: np.array, *, method = "bilateral", parameters: Parameters = None) -> np.array:
    
    if parameters:
        
        method = parameters.filter_type
    
    valid_methods: tuple[str] = ("bilateral", "gaussian", "non-local means", "tv bregman", "tv chambolle", "wavelet")
    
    if any(x == method for x in valid_methods):
        
        if method == "bilateral":
            
            dn_array: np.array = np.empty(im_array.shape, im_array.dtype)
            
            if parameters:
                
                for n in range(0, im_array.shape[0]):
                    
                    dn_array[n] = pixels.convert_im_type(restoration.denoise_bilateral(im_array[n],
                                                                                       win_size = parameters.win_size,
                                                                                       sigma_color = parameters.sigma_color,
                                                                                       sigma_spatial = parameters.sigma_spatial,
                                                                                       bins = parameters.bins,
                                                                                       mode = parameters.mode,
                                                                                       cval = parameters.cval,
                                                                                       channel_axis = parameters.channel_axis),
                                                         im_array.dtype)
            
            else:
                
                for n in range(0, im_array.shape[0]):
                    
                    dn_array[n] = pixels.convert_im_type(restoration.denoise_bilateral(im_array[n]),
                                                         im_array.dtype)
                    
        elif method == "gaussian":
            
            if parameters:
                
                dn_array: np.array = pixels.convert_im_type(filters.gaussian(im_array,
                                                                             sigma = parameters.sigma,
                                                                             mode = parameters.mode,
                                                                             cval = parameters.cval,
                                                                             preserve_range = parameters.preserve_range,
                                                                             truncate = parameters.truncate,
                                                                             channel_axis = parameters.channel_axis,
                                                                             out = parameters.out),
                                                            im_array.dtype)
            
            else:
            
                dn_array: np.array = pixels.convert_im_type(filters.gaussian(im_array), im_array.dtype)
        
        elif method == "non-local means":
            
            if parameters:
                
                dn_array: np.array = pixels.convert_im_type(restoration.denoise_nl_means(im_array,
                                                                    patch_size = parameters.patch_size,
                                                                    patch_distance = parameters.patch_distance,
                                                                    h = parameters.h,
                                                                    fast_mode = parameters.fast_mode,
                                                                    sigma = parameters.sigma,
                                                                    preserve_range = parameters.preserve_range,
                                                                    channel_axis = parameters.channel_axis),
                                       im_array.dtype)
            
            else:
            
                dn_array: np.array = pixels.convert_im_type(restoration.denoise_nl_means(im_array, fast_mode = True), im_array.dtype)
        
        elif method == "tv bregman":
            
            if parameters:
                
                dn_array: np.array = pixels.convert_im_type(restoration.denoise_tv_bregman(im_array,
                                                                                           weight = parameters.weight,
                                                                                           max_num_iter = parameters.max_num_iter,
                                                                                           eps = parameters.eps,
                                                                                           isotropic = parameters.isotropic,
                                                                                           channel_axis = parameters.channel_axis), im_array.dtype)
            
            else:
            
                dn_array: np.array = pixels.convert_im_type(restoration.denoise_tv_bregman(im_array), im_array.dtype)
                
        elif method == "tv chambolle":
            
            if parameters:
                
                dn_array: np.array = pixels.convert_im_type(restoration.denoise_tv_chambolle(im_array,
                                                                                             weight = parameters.weight,
                                                                                             eps = parameters.eps,
                                                                                             max_num_iter = parameters.max_num_iter,
                                                                                             channel_axis = parameters.channel_axis), im_array.dtype)
            
            else:
            
                dn_array: np.array = pixels.convert_im_type(restoration.denoise_tv_chambolle(im_array), im_array.dtype)
        
        elif method == "wavelet":
            
            if parameters:
                
                dn_array: np.array = pixels.convert_im_type(restoration.denoise_wavelet(im_array,
                                                                                        sigma = parameters.sigma,
                                                                                        wavelet = parameters.wavelet,
                                                                                        mode = parameters.mode,
                                                                                        wavelet_levels = parameters.wavelet_levels,
                                                                                        convert2ycbcr = parameters.convert2ycbcr,
                                                                                        method = parameters.method,
                                                                                        rescale_sigma = parameters.rescale_sigma,
                                                                                        channel_axis = parameters.channel_axis),
                                                            im_array.dtype)
            
            else:
            
                dn_array: np.array = pixels.convert_im_type(restoration.denoise_wavelet(im_array), im_array.dtype)
        
        return dn_array
    
    else:
        
        print("\nInvalid denoising method!")
        
def rank(im_array: np.array, *, parameters: Parameters = None) -> np.array:
    
    pass

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