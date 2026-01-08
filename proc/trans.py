"""
Module for image transformation operations
"""

# Imports

import numpy as np
import pixels

from skimage import transform


# Functions

def rotate(im_array: np.array, angle: float, direction: str = "CCW", *, resize: bool = False) -> np.array:
    
    valid_directions: tuple[str] = ("CW", "CCW")
    
    if any(x == direction for x in valid_directions):
        
        if direction == "CCW":
            
            rot_array: np.array = pixels.convert_im_type(np.moveaxis(transform.rotate(np.moveaxis(im_array, 0, 2), angle, resize = resize), 2, 0), im_array.dtype)
        
        elif direction == "CW":
            
            rot_array: np.array = pixels.convert_im_type(np.moveaxis(transform.rotate(np.moveaxis(im_array, 0, 2), -angle, resize = resize), 2, 0), im_array.dtype)
        
        return rot_array
    
    else:
        
        print("\nInvalid rotation direction!")

def mirror(im_array: np.array, direction: str = "vertical") -> np.array:
    
    valid_directions: tuple[str] = ("vertical", "horizontal", "through")
    
    if any(x == direction for x in valid_directions):
    
        if direction == "vertical":
            
            mir_array: np.array = np.moveaxis(np.flipud(np.moveaxis(im_array, 0, 2)), 2, 0)
        
        elif direction == "horizontal":
            
            mir_array: np.array = np.moveaxis(np.fliplr(np.moveaxis(im_array, 0, 2)), 2, 0)
        
        elif direction == "through":
            
            mir_array: np.array = np.moveaxis(np.flip(np.moveaxis(im_array, 0, 2), 2), 2, 0)
        
        return mir_array
        
    else:
        
        print("\nInvalid mirror direction!")

def reslice(im_array: np.array, orientation: str = "top") -> np.array:
    
    valid_orientations: tuple[str] = ("left", "right", "top", "bottom", "back")
    
    if any(x == orientation for x in valid_orientations):
    
        if orientation == "left":
            
            res_array: np.array = mirror(np.swapaxes(im_array, 0, 2), "horizontal")
        
        elif orientation == "right":
            
            res_array: np.array = mirror(np.swapaxes(im_array, 0, 2), "through")
        
        elif orientation == "top":
            
            res_array: np.array = mirror(np.swapaxes(im_array, 0, 1), "vertical")
        
        elif orientation == "bottom":
            
            res_array: np.array = mirror(np.swapaxes(im_array, 0, 1), "through")
        
        elif orientation == "back":
            
            res_array: np.array = mirror(mirror(im_array, "through"), "horizontal")
        
        return res_array
        
    else:
        
        print("\nInvalid reslice orientation!")

def translate(im_array: np.array, trans_vector: tuple[int], *, x_direction: str = "right", y_direction: str = "down") -> np.array:
    
    if x_direction == "right":
        
        trans_vector = (-trans_vector[0], trans_vector[1])
        
    if y_direction == "down":
        
        trans_vector = (trans_vector[0], -trans_vector[1])
    
    translation_matrix: transform.AffineTransform = transform.AffineTransform(translation = trans_vector)
    
    if len(im_array.shape) == 2:
        
        return pixels.convert_im_type(transform.warp(im_array, translation_matrix), im_array.dtype)
    
    else:
        
        trans_array: np.array = np.empty(im_array.shape)
        
        for n in range(0, im_array.shape[0]):
            
            trans_array[n] = transform.warp(im_array[n], translation_matrix)
            
        return pixels.convert_im_type(trans_array, im_array.dtype)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()