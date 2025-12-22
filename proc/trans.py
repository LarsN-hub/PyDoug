"""
Module for transforming images
"""

# Imports

import numpy as np


# Functions

def mirror(im_array: np.array, direction: str) -> np.array:
    
    valid_directions: tuple[str] = ("vertical", "horizontal", "through")
    
    if any(x == direction for x in valid_directions):
    
        if direction == "vertical":
            
            mir_array: np.array = np.flipud(im_array)
        
        elif direction == "horizontal":
            
            mir_array: np.array = np.fliplr(im_array)
        
        elif direction == "through":
            
            mir_array: np.array = np.flip(im_array, 2)
        
        return mir_array
        
    else:
        
        print("\nInvalid mirror direction!")

def reslice(im_array: np.array, orientation: str) -> np.array:
    
    valid_orientations: tuple[str] = ("left", "right", "top", "bottom", "back")
    
    if any(x == orientation for x in valid_orientations):
    
        if orientation == "left":
            
            res_array: np.array = mirror(np.swapaxes(im_array, 1, 2), "horizontal")
        
        elif orientation == "right":
            
            res_array: np.array = mirror(np.swapaxes(im_array, 1, 2), "through")
        
        elif orientation == "top":
            
            res_array: np.array = mirror(np.swapaxes(im_array, 0, 2), "vertical")
        
        elif orientation == "bottom":
            
            res_array: np.array = mirror(np.swapaxes(im_array, 0, 2), "through")
        
        elif orientation == "back":
            
            res_array: np.array = mirror(mirror(im_array, "through"), "horizontal")
        
        return res_array
        
    else:
        
        print("\nInvalid reslice orientation!")

def rotate(im_array: np.array, ccw_angle: float, expand_dim: bool = False) -> np.array:
    
    pass

def translate(im_array: np.array, trans_vector: tuple[int], expand_dim: bool = False) -> np.array:
    
    pass


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()