"""
Module for batch processing of images from pre-made parameters
"""


# Imports

import numpy as np
import shutil
import os

import readwrite as rw
import cropclip as cc
import trans

from segment import detect


# Functions

def apply_parameters(im_array: np.ndarray, parameters_dict: dict[str, list, np.ndarray]) -> np.ndarray:
    
    parameters_log: list[dict] = parameters_dict["Parameters"]
    
    for parameter in parameters_log:
        
        #########################
        # Manipulate Operations #
        #########################
        
        if parameter["Name"].find("Trimmed") == 0:
            
            print("Trimming...")
            
            if parameter["X Bounds"].lower() == "true":
                
                x_bounds: list = [int(parameter["X Min"]), int(parameter["X Max"])]
                
            else:
                
                x_bounds: None = None
                
            if parameter["Y Bounds"].lower() == "true":
                
                y_bounds: list = [int(parameter["Y Min"]), int(parameter["Y Max"])]
                
            else:
                
                y_bounds: None = None
                
            if parameter["Z Bounds"].lower() == "true":
                
                z_bounds: list = [int(parameter["Z Min"]), int(parameter["Z Max"])]
                
            else:
                
                z_bounds: None = None
                
            if parameter["Bounds as Slices"].lower() == "true":
                
                bounds_as_slices: bool = True
                
            else:
                
                bounds_as_slices: bool = False
                
            bounds_dict = {"X": x_bounds, "Y": y_bounds, "Z": z_bounds}
            im_array = cc.trim(im_array,
                               bounds_dict = bounds_dict,
                               bounds_as_slices = bounds_as_slices,
                               conserve_mem = True)
        
        elif parameter["Name"].find("Padded") == 0:
            
            print("Padding...")
            
            if parameter["X Bounds"].lower() == "true":
                
                x_bounds: list = [int(parameter["X Min"]), int(parameter["X Max"])]
                
            else:
                
                x_bounds: None = None
                
            if parameter["Y Bounds"].lower() == "true":
                
                y_bounds: list = [int(parameter["Y Min"]), int(parameter["Y Max"])]
                
            else:
                
                y_bounds: None = None
                
            if parameter["Z Bounds"].lower() == "true":
                
                z_bounds: list = [int(parameter["Z Min"]), int(parameter["Z Max"])]
                
            else:
                
                z_bounds: None = None
                
            if parameter["Bounds as Slices"].lower() == "true":
                
                bounds_as_slices: bool = True
                
            else:
                
                bounds_as_slices: bool = False
                
            if np.issubdtype(im_array.dtype, np.floating):
                
                padded_color: float = float(parameter["Padded Color"])
                
            else:
                
                padded_color: int = int(parameter["Padded Color"])
                
            bounds_dict: dict = {"X": x_bounds, "Y": y_bounds, "Z": z_bounds}
            im_array = cc.pad(im_array,
                              bounds_dict = bounds_dict,
                              bounds_as_slices = bounds_as_slices,
                              padded_color = padded_color,
                              conserve_mem = True)
        
        elif parameter["Name"].find("Masked") == 0:
            
            print("Masking...")
            
            if np.issubdtype(im_array.dtype, np.floating):
                
                mask_color: float = float(parameter["Masked Color"])
                
            else:
                
                mask_color: int = int(parameter["Masked Color"])
                
            mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
            im_array = cc.mask(im_array, mask_array,
                               method = parameter["Method"],
                               mask_color = mask_color,
                               conserve_mem = True)
        
        elif parameter["Name"].find("Cropped") == 0:
            
            print("Cropping...")
            
            if np.issubdtype(im_array.dtype, np.floating):
                
                mask_color: float = float(parameter["Masked Color"])
                
            else:
                
                mask_color: int = int(parameter["Masked Color"])
            
            mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
            im_array = cc.crop(im_array, mask_array,
                               mask_color = mask_color,
                               conserve_mem = True)
        
        
        ########################
        # Transform Operations #
        ########################
        
        elif parameter["Name"].find("Resliced") == 0:
            
            print("Reslicing...")
            im_array = trans.reslice(im_array, parameter["Orientation"])
        
        elif parameter["Name"].find("Rotated") == 0:
            
            print("Rotating...")
            
            if parameter["Resize"].lower() == "true":
                
                resize: bool = True
                
            else:
                
                resize: bool = False
            
            if parameter["Clockwise"].lower() == "true":
                
                im_array = trans.rotate(im_array, float(parameter["Angle"]),
                                        "CW", resize = resize)
                
            else:
                
                im_array = trans.rotate(im_array, float(parameter["Angle"]),
                                        resize = resize)
        
        elif parameter["Name"].find("Mirrored") == 0:
            
            print("Mirroring...")
            im_array = trans.mirror(im_array, int(parameter["Direction"]))
        
        elif parameter["Name"].find("Rescaled") == 0:
            
            print("Rescaling...")
            im_array = trans.rescale(im_array, float(parameter["Scale"]))
        
        
        ###########################
        # Pixel Values Operations #
        ###########################
        
        elif parameter["Name"].find("Converted") == 0:
            
            print("Converting type...")
        
        elif parameter["Name"].find("Normalized") == 0:
            
            print("Normalizing...")
        
        elif parameter["Name"].find("Saturated") == 0:
            
            print("Saturating...")
        
        elif parameter["Name"].find("Equalized") == 0:
            
            print("Equalizing...")
        
        elif parameter["Name"].find("Inverted") == 0:
            
            print("Inverting...")
        
        elif parameter["Name"].find("Re-assigned") == 0:
            
            print("Re-assigning...")
        
        
        ########################
        # Denoising Operations #
        ########################
        
        elif parameter["Name"].find("Bilateral") == 0:
            
            print("Bilateral filter...")
        
        elif parameter["Name"].find("Gaussian") == 0:
            
            print("Gaussian blur...")
        
        elif parameter["Name"].find("Non-Local Means") == 0:
            
            print("Non-local means filter...")
        
        elif parameter["Name"].find("Removed Background") == 0:
            
            print("Removing background...")
        
        elif parameter["Name"].find("TV Bregman") == 0:
            
            print("TV Bregman filter...")
        
        elif parameter["Name"].find("TV Chambolle") == 0:
            
            print("TV Chambolle filter...")
        
        elif parameter["Name"].find("Wavelet") == 0:
            
            print("Wavelet filter...")
        
        
        ###########################
        # Segmentation Operations #
        ###########################
        
        elif parameter["Name"].find("Manual Threshold") == 0:
            
            print("Manual thresholding...")
        
        elif parameter["Name"].find("Histogram Threshold") == 0:
            
            print("Histogram thresholding...")
        
        elif parameter["Name"].find("Local Threshold") == 0:
            
            print("Local thresholding...")
        
        elif parameter["Name"].find("Label") == 0:
            
            print("Connectivity labelling...")
        
        elif parameter["Name"].find("Watershed") == 0:
            
            print("Watershed labelling...")
            
            if parameter["Apply Mask"]:
                
                mask_array = parameters_dict[parameter["Mask Used"]]
                
            else:
                
                mask_array = None
                
            if parameter["Along Axis"].lower() == "true":
                
                along_axis: bool = True
                
            else:
                
                along_axis: bool = False
                
            im_array = detect.watershed(im_array,
                                        mask_array = mask_array,
                                        background = float(parameter["Background"]),
                                        connectivity = int(parameter["Connectivity"]),
                                        compactness = float(parameter["Watershed Compactness"]),
                                        along_axis = along_axis,
                                        axis = int(parameter["Axis"]))
        
        elif parameter["Name"].find("Random Walk") == 0:
            
            print("Random walk thresholding...")
        
        elif parameter["Name"].find("Morph Snakes") == 0:
            
            print("Morphological snakes thresholding...")
        
        
        #####################
        # Filter Operations #
        #####################
        
        elif parameter["Name"].find("Remove Objects") == 0:
            
            print("Removing objects...")
        
        elif parameter["Name"].find("Dilation") == 0:
            
            print("Dilating...")
        
        elif parameter["Name"].find("Erosion") == 0:
            
            print("Eroding...")
        
        elif parameter["Name"].find("Closing") == 0:
            
            print("Closing...")
        
        elif parameter["Name"].find("Opening") == 0:
            
            print("Opening...")
        
        elif parameter["Name"].find("Top Hat") == 0:
            
            print("Top hat...")
        
        elif parameter["Name"].find("Edge Detection") == 0:
            
            print("Detecting edges...")
        
        elif parameter["Name"].find("Corner Detection") == 0:
            
            print("Detecting corners...")
        
        elif parameter["Name"].find("Ring Removal") == 0:
            
            print("Removing rings...")
        
        elif parameter["Name"].find("FFT") == 0:
            
            print("Computing FFT...")
        
        
        #######################
        # Analysis Operations #
        #######################
        
        elif parameter["Name"].find("Histogram Plot") == 0:
            
            print("Generating histogram...")
        
        elif parameter["Name"].find("Line Scan") == 0:
            
            print("Generating line scan...")
        
        elif parameter["Name"].find("Gray Level Plot") == 0:
            
            print("Generating gray levels plot...")
        
        elif parameter["Name"].find("Misc Calculations") == 0:
            
            print("Performing calculations...")
        
        elif parameter["Name"].find("Axis Distribution Plot") == 0:
            
            print("Generating axial distribution...")
        
        elif parameter["Name"].find("Domain Size Distribution Plot") == 0:
            
            print("Generating domain size distribution...")
        
        elif parameter["Name"].find("Heat Map") == 0:
            
            print("Generating heat map...")
        
    
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