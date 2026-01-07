# -*- coding: utf-8 -*-
"""
Module for analysis of segmented images
"""

# Imports

import numpy as np

from skimage import measure


# Functions

def label(seg_array: np.array) -> np.array:
    
    return measure.label(seg_array)


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()