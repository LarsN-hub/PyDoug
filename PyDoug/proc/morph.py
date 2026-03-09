"""
Module for altering morphology of image features
"""


# Imports

import numpy as np

from skimage import morphology

from PyDoug.proc import pixels, util, thresh


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
            
            return morphology.ball(self.radius)
        
        elif self.footprint_type == "diamond":
            
            return morphology.diamond(self.radius)
        
        elif self.footprint_type == "disk":
            
            return morphology.disk(self.radius)
        
        elif self.footprint_type == "ellipse":
            
            return morphology.ellipse(self.width, self.height)
        
        elif self.footprint_type == "octagon":
            
            return morphology.octagon(self.m, self.n)
        
        elif self.footprint_type == "octahedron":
            
            return morphology.octahedron(self.radius)
        
        elif self.footprint_type == "star":
            
            return morphology.star(self.a)


# Functions

def remove_objects(im_array: np.ndarray, size: float | int,
                   mode: str = "particles", *,
                   mask_array: np.ndarray = None,
                   background: float | int = 0,
                   pixel_size: float | int = 1.0,
                   connectivity: int = None,
                   along_axis: bool = False,
                   axis: int = 0) -> np.ndarray:
    
    if im_array.dtype != np.int64 and mode == "particles":
        
        rem_array: np.ndarray = thresh.label(im_array, connectivity = connectivity, mask_array = mask_array, background = background, positional = along_axis, axis = axis)
        
    elif im_array.dtype != np.bool and mode == "holes":
        
        rem_array: np.ndarray = pixels.convert_im_type(im_array, "bool")
        
    else:
        
        rem_array = np.copy(im_array)
    
    if not connectivity:
        
        if im_array.ndim > 2 and not along_axis:
            
            connectivity = 3
            
        else:
            
            connectivity = 2
            
    if pixel_size != 1.0:
        
        size = round(size / pixel_size)
        
    if along_axis:
        
        proc_array: np.ndarray = util.get_along_axis_array(rem_array, axis)
        rem_array: np.ndarray = np.empty(proc_array.shape, proc_array.dtype)
        
        for n in range(0, proc_array.shape[0]):
            
            if mode == "particles":
                
                rem_array[n] = morphology.remove_small_objects(proc_array[n], connectivity = connectivity, max_size = size)
            
            elif mode == "holes":
                
                rem_array[n] = morphology.remove_small_holes(proc_array[n], connectivity = connectivity, max_size = size)
                
            rem_array = util.undo_axial_array(rem_array, axis)
    
    else:
        
        if mode == "particles":
                
            rem_array = morphology.remove_small_objects(rem_array, connectivity = connectivity, max_size = size)
        
        elif mode == "holes":
            
            rem_array = morphology.remove_small_holes(rem_array, connectivity = connectivity, max_size = size)
    
    if im_array.dtype != np.int64 and mode == "particles":
        
        return thresh.threshold(rem_array, 0)
    
    elif mode == "holes":
        
        return pixels.convert_im_type(rem_array, "uint8")
    
    else:
        
        return rem_array

def dilation(im_array: np.ndarray, n_iterations: int = 1, *,
             footprint: np.ndarray = None,
             along_axis: bool = False) -> np.ndarray:
    
    dil_array: np.ndarray = np.empty(im_array.shape, im_array.dtype)
    
    if along_axis:
        
        for i in range(0, n_iterations):
            
            if i == 0:
        
                for n in range(0, im_array.shape[0]):
                
                    dil_array[n] = morphology.dilation(im_array[n], footprint)
                    
            else:
                
                for n in range(0, im_array.shape[0]):
                
                    dil_array[n] = morphology.dilation(dil_array[n], footprint)
    
    else:
        
        for i in range(0, n_iterations):
            
            if i == 0:
    
                dil_array = morphology.dilation(im_array, footprint)
                
            else:
                
                dil_array = morphology.dilation(dil_array, footprint)
                
    return dil_array

def erosion(im_array: np.ndarray, n_iterations: int = 1, *,
            footprint: np.ndarray = None,
            along_axis: bool = False) -> np.ndarray:
    
    ero_array: np.ndarray = np.empty(im_array.shape, im_array.dtype)
    
    if along_axis:
        
        for i in range(0, n_iterations):
            
            if i == 0:
        
                for n in range(0, im_array.shape[0]):
                
                    ero_array[n] = morphology.erosion(im_array[n], footprint)
                    
            else:
                
                for n in range(0, im_array.shape[0]):
                
                    ero_array[n] = morphology.erosion(ero_array[n], footprint)
    
    else:
        
        for i in range(0, n_iterations):
            
            if i == 0:
    
                ero_array = morphology.erosion(im_array, footprint)
                
            else:
                
                ero_array = morphology.erosion(ero_array, footprint)
                
    return ero_array

def opening(im_array: np.ndarray, n_erosions: int = 1, n_dilations: int = 1, *,
            footprint: np.ndarray = None,
            along_axis: bool = False) -> np.ndarray:
    
    open_array: np.ndarray = np.copy(im_array)
    open_array = erosion(open_array, n_erosions, footprint = footprint, along_axis = along_axis)
    open_array = dilation(open_array, n_dilations, footprint = footprint, along_axis = along_axis)
        
    return open_array

def closing(im_array: np.ndarray, n_dilations: int = 1, n_erosions: int = 1, *,
            footprint: np.ndarray = None,
            along_axis: bool = False) -> np.ndarray:
    
    close_array: np.ndarray = np.copy(im_array)
    close_array = dilation(close_array, n_dilations, footprint = footprint, along_axis = along_axis)
    close_array = erosion(close_array, n_erosions, footprint = footprint, along_axis = along_axis)
        
    return close_array

def tophat(im_array: np.ndarray, method: str = "Black", n_dilations: int = 1, n_erosions: int = 1, *,
           footprint: np.ndarray = None,
           along_axis: bool = False) -> np.ndarray:
    
    if method == "Black":
        
        return closing(im_array, n_dilations = n_dilations, n_erosions = n_erosions, footprint = footprint, along_axis = along_axis) - im_array
    
    elif method == "White":
        
        return im_array - opening(im_array, n_dilations = n_dilations, n_erosions = n_erosions, footprint = footprint, along_axis = along_axis)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()