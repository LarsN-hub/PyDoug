"""
Module for import/export of image, parameter, and plot files
"""

# Imports

import tkfilebrowser as tkfb
import numpy as np
import platform
import skimage
import h5py
import os

from timeit import default_timer as timer
from PIL import Image


# Globals

write_exts: list[str] = ["png", "tif", "tiff"]
h5_exts: list[str] = ["h5", "hdf", "hdf5", "he5"]
valid_exts: list[str] = h5_exts + ["apng",
                                  "avif",
                                  "blp",
                                  "bmp",
                                  "cur",
                                  "dcx",
                                  "dds",
                                  "dib",
                                  "emf",
                                  "eps",
                                  "fits",
                                  "flc",
                                  "fli",
                                  "fpx",
                                  "ftex",
                                  "gbr",
                                  "gd2",
                                  "gif",
                                  "icb",
                                  "icns",
                                  "ico",
                                  "im",
                                  "imt",
                                  "iptc",
                                  "jpg",
                                  "jpeg",
                                  "jpe",
                                  "jif",
                                  "jfif",
                                  "jfi",
                                  "jp2",
                                  "j2k",
                                  "jpf",
                                  "jpm",
                                  "jpg2",
                                  "j2c",
                                  "jpc",
                                  "jpx",
                                  "mic",
                                  "mj2",
                                  "mpo",
                                  "msp",
                                  "pcd",
                                  "pcx",
                                  "pfm",
                                  "png",
                                  "pbm",
                                  "pgm",
                                  "ppm",
                                  "pnm",
                                  "psd",
                                  "qoi",
                                  "rgb",
                                  "sgi",
                                  "spi",
                                  "sun",
                                  "tga",
                                  "tif",
                                  "tiff",
                                  "vda",
                                  "vst",
                                  "wal",
                                  "webp",
                                  "wmf",
                                  "xbm",
                                  "xpm"
                                  "xv"]


# Functions

def universalize_paths(file_paths: str | list[str]) -> str | list[str]:
    
    if platform.system() == "Windows":
        
        if isinstance(file_paths, str):
        
            file_paths = file_paths.replace("\\", "/")
            
        elif isinstance(file_paths, list):
            
            for index, path in enumerate(file_paths):
                
                file_paths[index] = path.replace("\\", "/")
                
    return file_paths

def get_path(directory = False) -> str:
    
    if directory:
        
        path: str = tkfb.askopendirname(title = "Select folder")
    
    else:
        
        path: str = tkfb.askopenfilename(title = "Select file")
    
    return universalize_paths(path)

def get_paths(directory = False) -> list[str]:
    
    if directory:
        
        paths: list[str] = tkfb.askopendirnames(title = "Select folder(s)")
    
    else:
        
        paths: list[str] = tkfb.askopenfilenames(title = "Select file(s)")   
         
    return universalize_paths(list(paths))

def get_ext(file_path: str) -> str:
    
    dot_location: int = file_path.rfind(".")
    
    if dot_location == -1:
        
        file_ext = "directory"
        
    else:
        
        file_ext: str = file_path[dot_location + 1:]
    
    return file_ext

def detect_valid_ext(file_path: str) -> bool:
    
    global valid_exts
    ext: str = get_ext(file_path)
    
    return any(x == ext for x in valid_exts)

def detect_valid_dir(dir_path: str) -> bool:
    
    global valid_exts
    dir_contents: list[str] = os.listdir(dir_path)
    
    for file in dir_contents:
        
        if any(x == get_ext(file) for x in valid_exts):
            
            return True
        
            break

def detect_h5(file_path: str) -> bool:
    
    global h5_exts
    ext: str = get_ext(file_path)
    
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

def get_largest_data(h5_file: h5py.File) -> str:
    
    possible_dirs: list[str] = expand_groups(h5_file, [], False)
    prev_bytes = 0
    
    for directory in possible_dirs:
        
        if h5_file[directory].nbytes > prev_bytes:
            
            current_largest: str = directory
            prev_bytes = h5_file[directory].nbytes
            
    return current_largest

def read_h5(file_path: str) -> np.array:
    
    h5_file: h5py.File = h5py.File(file_path)
    dataset_dir: str = get_largest_data(h5_file)
    im_array = np.array(h5_file[dataset_dir])
    h5_file.close()
    
    return im_array

def read_im(file_path: str) -> np.array:
    
    if detect_valid_ext(file_path):
        
        if detect_h5(file_path):
            
            im_array: np.array = read_h5(file_path)
        
        else:
            
            try:
            
                im_array: np.array = skimage.io.imread(file_path)
                
            except OSError:
                
                im_array: np.array = np.array(Image.open(file_path))
        
        return im_array
            
    else:
            
        print("\nInvalid image file extension!")
        
        return None

def get_dir_stack_info(dir_path: str) -> dict:
    
    global valid_exts
    global h5_exts
    dir_contents: list[str] = os.listdir(dir_path)
    index_list = [np.nan, np.nan]
    
    for index, file in enumerate(dir_contents):
        
        if detect_valid_ext(file):
            
            index_list[0] = index
            
            break
        
    rev_dir = dir_contents.copy()
    rev_dir.reverse()
    
    for index, file in enumerate(rev_dir):
        
        if detect_valid_ext(file):
            
            index_list[1] = -1 * (index + 1)
            
            break
    
    ext = get_ext(dir_contents[index_list[0]])
    
    if any(x == ext for x in h5_exts):
        
        im_array_shape: None = None
        
    else:
        
        first_im_array: np.array = read_im(dir_path + "/" + dir_contents[index_list[0]])
        no_slices: int = len(dir_contents) + index_list[1] + 1 - index_list[0]
        im_array_shape = (first_im_array.shape[0], first_im_array.shape[1], no_slices)
    
    return {"Start": index_list[0],
            "End": index_list[1],
            "Shape": im_array_shape,
            "Extension": ext,
            "List": dir_contents}

def read_stack_slow(stack_path: str, h5_concat_axis = 0) -> np.array:
    
    if get_ext(stack_path) == "directory":
        
        dir_stack_info: dict = get_dir_stack_info(stack_path)
        im_array_shape = dir_stack_info["Shape"]
    
        if dir_stack_info["End"] == -1:
                
            dir_contents = dir_stack_info["List"][dir_stack_info["Start"]:]
                
        else:
                
            dir_contents = dir_stack_info["List"][dir_stack_info["Start"]:(dir_stack_info["End"] + 1)]
            
        if im_array_shape:
            
            im_array = np.empty(im_array_shape)
        
            for index, file in enumerate(dir_contents):
                
                im_array[:, :, index] = read_im(stack_path + "/" + file)
        
        else:
            
            for index, file in enumerate(dir_contents):
                
                if index == 0:
                    
                    im_array: np.array = read_h5(stack_path + "/" + file)
                    
                else:
                    
                    int_array: np.array = read_h5(stack_path + "/" + file)
                    im_array = np.concat([im_array, int_array], axis = h5_concat_axis)
    
    else:
        
        if detect_h5(stack_path):
            
            im_array: np.array = read_h5(stack_path)
                
        else:
        
            im = Image.open(stack_path)
            no_rows, no_cols = np.shape(im)
            im_array = np.empty((no_rows, no_cols, im.n_frames))
            
            for i in range(0, (im.n_frames + 1)):
                
               im.seek(i)
               im_array[:, :, i] = np.array(im)   
    
    return im_array

def read_stack_fast(stack_path: str) -> np.array:
    
    if get_ext(stack_path) == "directory":
        
        dir_contents: list[str] = os.listdir(stack_path)
        
        for index, file in enumerate(dir_contents):
            
            dir_contents[index] = stack_path + "/" + file
            
        im_collection: skimage.io.ImageCollection = skimage.io.imread_collection(dir_contents)
        im_array: np.array = skimage.io.concatenate_images(im_collection)
        
    else:
        
        im_collection: skimage.io.MultiImage = skimage.io.MultiImage(stack_path)
        im_array: np.array = skimage.io.concatenate_images(im_collection)
    
    return np.moveaxis(np.squeeze(im_array), 0, 2)
    
def read_stack(stack_path: str) -> np.array:
    
    ext = get_ext(stack_path)
    
    if ext == "directory":
        
        valid = detect_valid_dir(stack_path)
        
    else:
        
        valid = detect_valid_ext(stack_path)
        
    if valid:
    
        start = timer()
        try:
            
            im_array: np.array = read_stack_fast(stack_path)
                
        except OSError:
            
            im_array: np.array = read_stack_slow(stack_path)
            
        end = timer()
        print(f"\nFinished import in {(end - start):.2} s!")
            
        return im_array
    
    else:
        
        print("\nInvalid image file extension!")
        
        return None
    
def write_h5(im_array: np.array, save_path: str) -> None:
    
    h5_file: h5py.File = h5py.File(save_path, "w")
    h5_file.create_dataset("im_array", data = im_array)
    h5_file.close()
    
def write_im(im_array: np.array, save_dir: str, file_name: str, ext: str = "tiff") -> None:
    
    global write_exts
    global h5_exts
    save_path: str = save_dir + "/" + file_name + "." + ext
    
    if any(ext == x for x in write_exts):
        
        skimage.io.imsave(save_path, im_array, check_contrast = False)
    
    elif any(ext == x for x in h5_exts):
        
        write_h5(im_array, save_path)
        
    else:
        
        print("\nInvalid image file extneion!")
        
def write_stack(im_array: np.array, save_dir: str, file_name: str, ext: str = "tiff", multi_page: bool = False) -> None:
    
    global write_exts
    global h5_exts
    save_path: str = save_dir + "/" + file_name + "." + ext
    
    if any(ext == x for x in write_exts):
        
        start = timer()
        
        if multi_page:
            
            save_path: str = save_dir + "/" + file_name + "." + ext
            skimage.io.imsave(save_path, np.moveaxis(im_array, 2, 0), check_contrast = False)
            
        else:
            
            os.makedirs(save_dir + "/" + file_name)
            no_slices: int = im_array.shape[2]
            
            for n in range(0, no_slices):
                
                save_path: str = save_dir + "/" + file_name + "/" + f"slice_{n:04}." + ext
                skimage.io.imsave(save_path, im_array[:, :, n], check_contrast = False)
                
        end = timer()
        print(f"\nFinished export in {(end - start):.2} s!")
    
    elif any(ext == x for x in h5_exts):
        
        start = timer()
        save_path: str = save_dir + "/" + file_name + "." + ext
        write_h5(im_array, save_path)
        end = timer()
        print(f"\nFinished export in {(end - start): .2} s!")
        
    else:
        
        print("\nInvalid image file extension!")


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()