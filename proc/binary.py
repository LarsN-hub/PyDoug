"""
Module for processing segmented images
"""

# Imports

import numpy as np

from skimage import morphology


# Functions

def particle_filter(seg_array: np.array, min_size: int, *, connectivity: int = 1) -> np.array:
    
    return morphology.remove_small_objects(seg_array, min_size = min_size, connectivity = connectivity)

def hole_filter(seg_array: np.array, max_size: int, *, connectivity: int = 1) -> np.array:
    
    return morphology.remove_small_holes(seg_array, max_size = max_size, connectivity = connectivity)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()