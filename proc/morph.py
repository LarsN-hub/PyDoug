"""
Module for altering morphology of image features
"""

# Imports

import numpy as np

from skimage import morphology


# Classes

class Footprint:
    
    def __init__(self, footprint_type: str) -> None:
        
        self.footprint_type = footprint_type
        
        if footprint_type == "ball":
            
            self.radius = 1
        
        elif footprint_type == "diamond":
            
            self.radius = 1
        
        elif footprint_type == "disk":
            
            self.radius = 1
        
        elif footprint_type == "ellipse":
            
            self.width = 1
            self.height = 1
        
        elif footprint_type == "octagon":
            
            self.m = 1
            self.n = 1
        
        elif footprint_type == "octahedron":
            
            self.radius = 1
        
        elif footprint_type == "star":
            
            self.a = 1
            
        else:
            
            print("\nInvalid footprint type!")
            
    def get_footprint(self) -> np.ndarray:
        
        if self.footprint_type == "ball":
            
            self.footprint = morphology.ball(self.radius)
        
        elif self.footprint_type == "diamond":
            
            self.footprint = morphology.diamond(self.radius)
        
        elif self.footprint_type == "disk":
            
            self.footprint = morphology.disk(self.radius)
        
        elif self.footprint_type == "ellipse":
            
            self.footprint = morphology.ellipse(self.width, self.height)
        
        elif self.footprint_type == "octagon":
            
            self.footprint = morphology.octagon(self.m, self.n)
        
        elif self.footprint_type == "octahedron":
            
            self.footprint = morphology.octahedron(self.radius)
        
        elif self.footprint_type == "star":
            
            self.footprint = morphology.star(self.a)


# Functions

def dilation(im_array: np.ndarray, *, footprint: np.ndarray = None, along_axis: bool = False) -> np.ndarray:
    
    if along_axis:
        
        dil_array: np.ndarray = np.empty(im_array.shape, im_array.dtype)
        
        for n in range(0, im_array.shape[0]):
            
            dil_array[n] = morphology.dilation(im_array[n], footprint)
            
        return dil_array
    
    else:
    
        return morphology.dilation(im_array, footprint)

def erosion(im_array: np.ndarray, *, footprint: np.ndarray = None, along_axis: bool = False) -> np.ndarray:
    
    if along_axis:
        
        erod_array: np.ndarray = np.empty(im_array.shape, im_array.dtype)
        
        for n in range(0, im_array.shape[0]):
            
            erod_array[n] = morphology.erosion(im_array[n], footprint)
            
        return erod_array
    
    else:
    
        return morphology.erosion(im_array, footprint)

def opening(im_array: np.ndarray, *, footprint: np.ndarray = None, along_axis: bool = False) -> np.ndarray:
    
    if along_axis:
        
        open_array: np.ndarray = np.empty(im_array.shape, im_array.dtype)
        
        for n in range(0, im_array.shape[0]):
            
            open_array[n] = morphology.opening(im_array[n], footprint)
            
        return open_array
    
    else:
    
        return morphology.opening(im_array, footprint)

def closing(im_array: np.ndarray, *, footprint: np.ndarray = None, along_axis: bool = False) -> np.ndarray:
    
    if along_axis:
        
        close_array: np.ndarray = np.empty(im_array.shape, im_array.dtype)
        
        for n in range(0, im_array.shape[0]):
            
            close_array[n] = morphology.closing(im_array[n], footprint)
            
        return close_array
    
    else:
    
        return morphology.closing(im_array, footprint)

def white_tophat(im_array: np.ndarray, *, footprint: np.ndarray = None, along_axis: bool = False) -> np.ndarray:
    
    return im_array - opening(im_array, footprint = footprint, along_axis = along_axis)

def black_tophat(im_array: np.ndarray, *, footprint: np.ndarray = None, along_axis: bool = False) -> np.ndarray:
    
    return closing(im_array, footprint = footprint, along_axis = along_axis) - im_array


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()