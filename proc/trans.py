"""
Module for image transformation operations
"""


# Imports

import numpy as np
import pixels

from skimage import transform


# Functions

def rotate(im_array: np.ndarray, angle: float, direction: str = "CCW", *, resize: bool = False, preserve_range: bool = False) -> np.ndarray:
    
    if direction == "CCW":
        
        if im_array.ndim > 2:
            
            rot_array: np.ndarray = np.moveaxis(transform.rotate(np.moveaxis(im_array, 0, 2), angle, resize = resize, preserve_range = preserve_range), 2, 0)
        
        else:
            
            rot_array: np.ndarray = transform.rotate(im_array, angle, resize = resize, preserve_range = preserve_range)
            
    elif direction == "CW":
        
        if im_array.ndim > 2:
            
            rot_array: np.ndarray = np.moveaxis(transform.rotate(np.moveaxis(im_array, 0, 2), -angle, resize = resize, preserve_range = preserve_range), 2, 0)
        
        else:
            
            rot_array: np.ndarray = transform.rotate(im_array, -angle, resize = resize, preserve_range = preserve_range)
        
    if preserve_range:
        
        return rot_array
    
    else:
        
        return pixels.convert_im_type(rot_array, im_array.dtype)

def mirror(im_array: np.ndarray, direction: int = 0) -> np.ndarray:
    
    if direction == 0:
        
        if im_array.ndim > 2:
        
            return np.moveaxis(np.flip(np.moveaxis(im_array, 0, 2), 2), 2, 0)
        
        else:
            
            return np.flip(im_array, 0)
    
    elif direction == 1:
        
        if im_array.ndim > 2:
            
            return np.moveaxis(np.flipud(np.moveaxis(im_array, 0, 2)), 2, 0)
        
        else:
            
            return np.flip(im_array, 1)
        
    elif direction == 2:
            
        return np.moveaxis(np.fliplr(np.moveaxis(im_array, 0, 2)), 2, 0)

def reslice(im_array: np.ndarray, orientation: str = "top") -> np.ndarray:
    
    if orientation == "left":
            
        return mirror(np.swapaxes(im_array, 0, 2), 2)
        
    elif orientation == "right":
            
        return mirror(np.swapaxes(im_array, 0, 2), 0)
        
    elif orientation == "top":
            
        return mirror(np.swapaxes(im_array, 0, 1), 1)
        
    elif orientation == "bottom":
            
        return mirror(np.swapaxes(im_array, 0, 1), 0)
        
    elif orientation == "back":
            
        return mirror(mirror(im_array, 0), 2)
    
def rescale(im_array: np.ndarray, scale: float) -> np.ndarray:
    
    if scale == 1:
        
        return im_array
    
    elif 1 > scale > 0:
        
        return pixels.convert_im_type(transform.rescale(im_array, scale, anti_aliasing = True), im_array.dtype)
    
    elif scale > 1:
        
        return pixels.convert_im_type(transform.rescale(im_array, scale), im_array.dtype)
    
    else:
        
        print("\nInvalid rescaling factor!")

def translate(im_array: np.ndarray, trans_vector: tuple[int], *, x_direction: str = "right", y_direction: str = "down") -> np.ndarray:
    
    if x_direction == "right":
        
        trans_vector = (-trans_vector[0], trans_vector[1])
        
    if y_direction == "down":
        
        trans_vector = (trans_vector[0], -trans_vector[1])
    
    translation_matrix: transform.AffineTransform = transform.AffineTransform(translation = trans_vector)
    
    if len(im_array.shape) == 2:
        
        return pixels.convert_im_type(transform.warp(im_array, translation_matrix), im_array.dtype)
    
    else:
        
        trans_array: np.ndarray = np.empty(im_array.shape)
        
        for n in range(0, im_array.shape[0]):
            
            trans_array[n] = transform.warp(im_array[n], translation_matrix)
            
        return pixels.convert_im_type(trans_array, im_array.dtype)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()