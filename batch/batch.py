"""
Module for batch processing of images from pre-made parameters
"""


# Imports

import numpy as np
import os

import readwrite as rw


# Functions


# Main

def main(directories: bool = False, copy_parameters: bool = True) -> None:
    
    if directories:
        
        title: str = "Select image folder(s)"
        
    else:
        
        title: str = "Select image file(s)"
    
    images_list: list[str] = rw.get_paths(directories, title)
    parameters_dict: dict[str, list, np.ndarray] = rw.read_parameters_dir(rw.get_path(True, "Select parameters directory"))
    save_dir: str = rw.get_path(True, "Select output directory")
    
    if copy_parameters:
        
        pass
    

if __name__ == "__main__":
    
    main()