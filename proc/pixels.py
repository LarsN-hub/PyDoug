"""
Module for altering pixel values and dimensions
"""

# Imports

import numpy as np

from skimage import util


# Functions

def data_type(im_array: np.array, convert_type: str) -> np.array:
    
    valid_types: tuple[str] = ("uint8", "uint16", "int16", "float", "float32", "float64", "bool")
    
    if any(x == convert_type for x in valid_types):
        
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


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()