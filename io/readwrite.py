"""
Module for import/export of image files
"""

# Imports

import tkfilebrowser as tkfb
import numpy as np
import h5py

from PIL import Image


# Functions

def get_path(directory = False) -> str:
    
    if directory:
        
        path: str = tkfb.askopendirname(title = "Select folder")
    
    else:
        
        path: str = tkfb.askopenfilename(title = "Select file")
    
    return path

def get_paths(directory = False) -> list[str]:
    
    if directory:
        
        paths: list[str] = tkfb.askopendirnames(title = "Select folder(s)")
    
    else:
        
        paths: list[str] = tkfb.askopenfilenames(title = "Select file(s)")   
         
    return paths

def get_ext(file_path: str) -> str:
    
    dot_location: int = file_path.rfind(".")
    file_ext: str = file_path[dot_location + 1:]
    
    return file_ext

def read_image(file_path: str) -> np.array:
    
    im_array: np.array = np.array(Image.open(file_path))
        
    return im_array

def detect_hdf5(file_path: str) -> bool:
    
    ext: str = get_ext(file_path)
    h5_exts: list[str] = ["h5", "hdf", "hdf5", "he5"]
    
    return any(x == ext for x in h5_exts)

def expand_groups(h5_object: h5py.File | h5py.Group, possible_dirs: list[str], readout: bool = False) -> list[str]:
    
    contents: list = list(h5_object.keys())
    
    if h5_object.name == "/":
        
        tab_count: int = 0
        
    else:
            
        tab_count: int = h5_object.name.count("/")
    
    for item in contents:
        
        label = h5_object[item].name[h5_object[item].name.rfind("/") + 1:]
        
        if isinstance(h5_object[item], h5py.Group):
            
            if readout:
                
                print((tab_count * "  ") + "- " + label)
                
            possible_dirs = expand_groups(h5_object[item], possible_dirs, readout)
        
        elif isinstance(h5_object[item], h5py.Dataset):
            
            if len(h5_object[item].shape):
                
                label = label + " [shape: " + str(h5_object[item].shape) + "]"
                possible_dirs.append(h5_object[item].name)
                
            if readout:
                
                print((tab_count * "  ") + "- " + label)
    
    return possible_dirs

def get_largest_data(h5_file: h5py.File, possible_dirs: list[str]) -> str:
    
    prev_bytes = 0
    
    for directory in possible_dirs:
        
        if h5_file[directory].nbytes > prev_bytes:
            
            current_largest: str = directory
            prev_bytes = h5_file[directory].nbytes
            
    return current_largest

def read_hdf5(file_path: str) -> np.array:
    
    h5_file: h5py.File = h5py.File(file_path)
    possible_dirs: list[str] = expand_groups(h5_file, [], False)
    data_dir: str = get_largest_data(h5_file, possible_dirs)
    im_array = np.array(h5_file[data_dir])
    h5_file.close()
    
    return im_array
    
def read_stack(stack_path: str) -> np.array:
    
    if detect_hdf5(stack_path):
        
        pass

# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()