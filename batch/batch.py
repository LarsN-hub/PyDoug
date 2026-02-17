"""
Module for batch processing of images from pre-made parameters
"""


# Imports

import numpy as np
import shutil
import os

import readwrite as rw
import cropclip as cc

from segment import detect


# Functions

def apply_parameters(im_array: np.ndarray, parameters_dict: dict[str, list, np.ndarray]) -> np.ndarray:
    
    parameters_log: list[dict] = parameters_dict["Parameters"]
    
    for parameter in parameters_log:
        
        
        #########################
        # Manipulate Operations #
        #########################
        
        if parameter["Name"].find("Trimmed") == 0:
            
            if parameter["X Bounds"]:
                
                x_bounds = [parameter["X Min"], parameter["X Max"]]
                
            else:
                
                x_bounds = None
                
            if parameter["Y Bounds"]:
                
                y_bounds = [parameter["Y Min"], parameter["Y Max"]]
                
            else:
                
                y_bounds = None
                
            if parameter["Z Bounds"]:
                
                z_bounds = [parameter["Z Min"], parameter["Z Max"]]
                
            else:
                
                z_bounds = None
                
            bounds_dict = {"X": x_bounds, "Y": y_bounds, "Z": z_bounds}
            print(bounds_dict)
            im_array = cc.trim(im_array,
                               bounds_dict = bounds_dict,
                               bounds_as_slices = parameter["Bounds as Slices"],
                               conserve_mem = True)
        
        elif parameter["Name"].find("Padded") == 0:
            
            if parameter["X Bounds"]:
                
                x_bounds = [parameter["X Min"], parameter["X Max"]]
                
            else:
                
                x_bounds = None
                
            if parameter["Y Bounds"]:
                
                y_bounds = [parameter["Y Min"], parameter["Y Max"]]
                
            else:
                
                y_bounds = None
                
            if parameter["Z Bounds"]:
                
                z_bounds = [parameter["Z Min"], parameter["Z Max"]]
                
            else:
                
                z_bounds = None
                
            bounds_dict = {"X": x_bounds, "Y": y_bounds, "Z": z_bounds}
            im_array = cc.pad(im_array,
                              bounds_dict = bounds_dict,
                              bounds_as_slices = parameter["Bounds as Slices"],
                              padded_color = parameter["Padded Color"],
                              conserve_mem = True)
        
        elif parameter["Name"].find("Masked") == 0:
            
            mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
            im_array = cc.mask(im_array, mask_array,
                               method = parameter["Method"],
                               mask_color = parameter["Masked Color"],
                               conserve_mem = True)
        
        elif parameter["Name"].find("Cropped") == 0:
            
            mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
            im_array = cc.crop(im_array, mask_array,
                               mask_color = parameter["Masked Color"],
                               conserve_mem = True)
        
        
        ########################
        # Transform Operations #
        ########################
        
        elif parameter["Name"].find("Resliced") == 0:
            
            pass
        
        elif parameter["Name"].find("Rotated") == 0:
            
            pass
        
        elif parameter["Name"].find("Mirrored") == 0:
            
            pass
        
        elif parameter["Name"].find("Rescaled") == 0:
            
            pass
        
        
        ###########################
        # Pixel Values Operations #
        ###########################
        
        elif parameter["Name"].find("Converted") == 0:
            
            pass
        
        elif parameter["Name"].find("Normalized") == 0:
            
            pass
        
        elif parameter["Name"].find("Saturated") == 0:
            
            pass
        
        elif parameter["Name"].find("Equalized") == 0:
            
            pass
        
        elif parameter["Name"].find("Inverted") == 0:
            
            pass
        
        elif parameter["Name"].find("Re-assigned") == 0:
            
            pass
        
        
        ########################
        # Denoising Operations #
        ########################
        
        elif parameter["Name"].find("Bilateral") == 0:
            
            pass
        
        elif parameter["Name"].find("Gaussian") == 0:
            
            pass
        
        elif parameter["Name"].find("Non-Local Means") == 0:
            
            pass
        
        elif parameter["Name"].find("Removed Background") == 0:
            
            pass
        
        elif parameter["Name"].find("TV Bregman") == 0:
            
            pass
        
        elif parameter["Name"].find("TV Chambolle") == 0:
            
            pass
        
        elif parameter["Name"].find("Wavelet") == 0:
            
            pass
        
        
        ###########################
        # Segmentation Operations #
        ###########################
        
        elif parameter["Name"].find("Manual Threshold") == 0:
            
            pass
        
        elif parameter["Name"].find("Histogram Threshold") == 0:
            
            pass
        
        elif parameter["Name"].find("Local Threshold") == 0:
            
            pass
        
        elif parameter["Name"].find("Label") == 0:
            
            pass
        
        elif parameter["Name"].find("Watershed") == 0:
            
            if parameter["Apply Mask"]:
                
                mask_array = parameters_dict[parameter["Mask Used"]]
                
            else:
                
                mask_array = None
                
            im_array = detect.watershed(im_array,
                                        mask_array = mask_array,
                                        background = parameter["Background"],
                                        connectivity = parameter["Connectivity"],
                                        compactness = parameter["Watershed Compactness"],
                                        along_axis = parameter["Along Axis"],
                                        axis = parameter["Axis"])
        
        elif parameter["Name"].find("Random Walk") == 0:
            
            pass
        
        elif parameter["Name"].find("Morph Snakes") == 0:
            
            pass
        
        
        #####################
        # Filter Operations #
        #####################
        
        elif parameter["Name"].find("Remove Objects") == 0:
            
            pass
        
        elif parameter["Name"].find("Dilation") == 0:
            
            pass
        
        elif parameter["Name"].find("Erosion") == 0:
            
            pass
        
        elif parameter["Name"].find("Closing") == 0:
            
            pass
        
        elif parameter["Name"].find("Opening") == 0:
            
            pass
        
        elif parameter["Name"].find("Top Hat") == 0:
            
            pass
        
        elif parameter["Name"].find("Edge Detection") == 0:
            
            pass
        
        elif parameter["Name"].find("Corner Detection") == 0:
            
            pass
        
        elif parameter["Name"].find("Ring Removal") == 0:
            
            pass
        
        elif parameter["Name"].find("FFT") == 0:
            
            pass
        
        
        #######################
        # Analysis Operations #
        #######################
        
        elif parameter["Name"].find("Histogram Plot") == 0:
            
            pass
        
        elif parameter["Name"].find("Line Scan") == 0:
            
            pass
        
        elif parameter["Name"].find("Gray Level Plot") == 0:
            
            pass
        
        elif parameter["Name"].find("Misc Calculations") == 0:
            
            pass
        
        elif parameter["Name"].find("Axis Distribution Plot") == 0:
            
            pass
        
        elif parameter["Name"].find("Domain Size Distribution Plot") == 0:
            
            pass
        
        elif parameter["Name"].find("Heat Map") == 0:
            
            pass
        
    
    return im_array


# Main

def main(format: str = "3D", stack_format: str = "Multi-Page", export_multi_page: bool = True, copy_parameters: bool = True) -> None:
    
    if stack_format == "Sequence":
        
        title: str = "Select image folder(s)"
        directories: bool = True
        
    else:
        
        title: str = "Select image file(s)"
        directories: bool = False
    
    im_list: list[str] = rw.get_paths(directories, title)
    parameters_path: str = rw.get_path(True, "Select parameters directory")
    parameters_dict: dict[str, list, np.ndarray] = rw.read_parameters_dir(parameters_path)
    save_dir: str = rw.get_path(True, "Select output directory")
    
    if copy_parameters:
        
        os.mkdir(save_dir + "/Parameters")
        shutil.copytree(parameters_path, save_dir + "/Parameters", dirs_exist_ok = True)
        
    for index, im_path in enumerate(im_list, 1):
        
        print(f"\nImporting dataset {index} of {len(im_list)}...")
        
        if rw.get_ext(im_path) == "directory":
            
            file_name: str = im_path[(im_path.rfind("/") + 1):]
            
        else:
            
            file_name: str = im_path[(im_path.rfind("/") + 1):im_path.rfind(".")]
        
        if format == "3D":
            
            im_array: np.ndarray = rw.read_stack(im_path)
        
        elif format == "2D":
            
            im_array: np.ndarray = rw.read_im(im_path)
            
        im_array = apply_parameters(im_array, parameters_dict)
        
        if format == "3D":
            
            rw.write_stack(im_array, save_dir, file_name, multi_page = export_multi_page)
        
        elif format == "2D":
            
            rw.write_im(im_array, save_dir, file_name)
            
    print("\nFinished batch processing!")
    

if __name__ == "__main__":
    
    main()