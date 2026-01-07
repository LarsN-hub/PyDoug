"""
Module for altering and assessing pixel values and dimensions
"""

# Imports

import numpy as np

from matplotlib import pyplot as plt
from skimage import transform
from skimage import exposure
from skimage import util


# Functions

def statistics(im_array: np.array) -> dict:
    
    im_stats: dict = {}
    im_stats["mean"] = float(np.mean(im_array))
    im_stats["median"] = float(np.median(im_array))
    im_stats["min"] = float(np.min(im_array))
    im_stats["max"] = float(np.max(im_array))
    im_stats["stdev"] = float(np.std(im_array))
    
    return im_stats

def histogram(im_array: np.array) -> plt.figure:
    
    counts, bin_centers = exposure.histogram(im_array)
    fig: plt.figure = plt.figure(dpi = 300)
    fax: plt.axes = plt.axes()
    fax.figure = fig
    fax.set_xlabel("Intensity")
    fax.set_ylabel("Counts")
    plt.hist(bin_centers, bin_centers, weights = counts, axes = fax)
    
    return fig

def saturate(im_array: np.array, bounds: tuple) -> np.array:
    
    im_array[im_array > max(bounds)] = max(bounds)
    im_array[im_array < min(bounds)] = min(bounds)
    
    return im_array

def normalize(im_array: np.array, norm_bounds: tuple) -> np.array:
    
    return np.astype((((im_array - im_array.min()) / (im_array.max() - im_array.min())) * (max(norm_bounds) - min(norm_bounds))) + min(norm_bounds), im_array.dtype)

def convert_im_type(im_array: np.array, convert_type: str, *, norm: bool = False, float_bounds: tuple[float] = None) -> np.array:
    
    valid_types: tuple[str] = ("uint8", "uint16", "int16", "float", "float32", "float64", "bool")
    
    if any(x == convert_type for x in valid_types):
        
        if str(im_array.dtype).find("float") != -1 and (norm or (np.max(im_array) > 1 or np.min(im_array) < -1)):
            
            if float_bounds:
                
                im_array = saturate(im_array, float_bounds);
            
            im_array = normalize(im_array, (-1, 1))
            
        if convert_type == "uint8":
                    
            conv_array: np.array = util.img_as_ubyte(im_array)
                
        elif convert_type == "uint16":
                    
            conv_array: np.array = util.img_as_uint(im_array)
                
        elif convert_type == "int16":
                    
            conv_array: np.array = util.img_as_int(im_array)
                
        elif convert_type == "float":
                    
            conv_array: np.array = util.img_as_float(im_array)
                    
        elif convert_type == "float32":
                    
            conv_array: np.array = util.img_as_float32(im_array)
                    
        elif convert_type == "float64":
                    
            conv_array: np.array = util.img_as_float64(im_array)
                
        elif convert_type == "bool":
                    
            conv_array: np.array = util.img_as_bool(im_array)
            
        return conv_array
        
    else:
            
        print("\nInvalid convert type!")
        
def rescale(im_array: np.array, scale: float) -> np.array:
    
    if scale == 1:
        
        return im_array
    
    elif 1 > scale > 0:
        
        return convert_im_type(transform.rescale(im_array, scale, anti_aliasing = True), im_array.dtype)
    
    elif scale > 1:
        
        return convert_im_type(transform.rescale(im_array, scale), im_array.dtype)
    
    else:
        
        print("\nInvalid rescaling factor!")
        
def invert(im_array: np.array) -> np.array:
    
    return util.invert(im_array)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()