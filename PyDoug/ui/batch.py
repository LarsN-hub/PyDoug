"""
Module for batch processing of images from pre-made parameters
"""


# Imports

import pandas as pd
import numpy as np
import napari
import shutil
import os

from timeit import default_timer as timer
from matplotlib import pyplot as plt

from PyDoug.ui import readwrite as rw, sliceview as sv
from PyDoug.proc import cropclip as cc, denoising, detect, fourier, morph, pixels, thresh, trans, util
from PyDoug.analyze import quant, plots


# Functions

def check_used_later(
        parameter_name: str,
        parameters_log: list[dict]) -> bool:
    
    if parameter_name == "Start":
        encountered_current_parameter = True
    else:
        encountered_current_parameter: bool = False
    encountered_later: bool = False
    
    for parameter in parameters_log:
        if not encountered_current_parameter:
            if parameter["Name"] == parameter_name:
                encountered_current_parameter = True
                
        else:
            if "Acting On" in list(parameter.keys()):
                if parameter["Acting On"] == parameter_name:
                    encountered_later = True
            if "Mask Used" in list(parameter.keys()):
                if parameter["Mask Used"] == parameter_name:
                    encountered_later = True
        
    return encountered_later

def check_in_parameters_dict(
        parameter_name: str,
        parameters_dict: dict) -> bool:
    
    if parameter_name in list(parameters_dict.keys()):
        return True
    else:
        return False

def apply_parameters(
        im_array: np.ndarray,
        parameters_dict: dict[str, list, np.ndarray],
        file_name: str = None,
        save_dir: str = None) -> np.ndarray:
    
    parameters_log: list[dict] = parameters_dict["Parameters"]
    screenshot_index: int = 0
    stats_index: int = 0
    quantity_index: int = 0
    surf_index: int = 0
    cont_index: int = 0
    frac_index: int = 0
    spec_index: int = 0
    res_index: int = 0
    hist_index: int = 0
    gray_index: int = 0
    axis_dist_index: int = 0
    psd_index: int = 0
    heat_index: int = 0
    cmaps: dict = {}
    
    for parameter_index, parameter in enumerate(parameters_log):
        if check_in_parameters_dict(
                parameter["Name"],
                parameters_dict):
            continue
        
        if parameter_index == 0:
            parameters_dict["Start"] = im_array
            parameter["Acting On"] = "Start"
            prev_name: str = parameter["Name"]
            last_image_name: str = "Start"
        else:
            if "Acting On" not in list(parameter.keys()):
                parameter["Acting On"] = prev_name
            prev_name: str = parameter["Name"]
            
        if check_used_later(
                parameter["Acting On"],
                parameters_log):
            im_array = parameters_dict[parameter["Acting On"]]
        else:
            im_array = parameters_dict.pop(parameter["Acting On"])
        
        
        ##################
        # I/O Operations #
        ##################
        
        if parameter["Name"].find("Screenshot") == 0:
            viewer: napari.viewer.Viewer = sv.create_viewer()
            viewer.window._qt_window.showFullScreen()
            viewer.dims.ndisplay = int(parameter["Dimensions"])
            
            if parameter["Layer Type"] == "labels":
                layer: napari.layers.Labels = viewer.add_labels(
                    parameters_dict[
                        parameter["Acting On"]])
                layer.iso_gradient_mode = parameter["ISO Gradient Mode"]
                layer.rendering = parameter["Rendering"]
                if parameter["Colormap Used"] != "label_colormap":
                    layer.colormap = cmaps[parameter["Acting On"]]
            
            elif parameter["Layer Type"] == "image":
                layer: napari.layers.Image = viewer.add_image(
                    parameters_dict[
                        parameter["Acting On"]])
                layer.colormap = parameter["Colormap"]
                layer.contrast_limits = (
                    float(parameter["Contrast Min"]),
                    float(parameter["Contrast Max"]))
                layer.gamma = float(parameter["Gamma"])
                layer.projection_mode = parameter["Projection Mode"]
                layer.rendering = parameter["Rendering"]
                layer.interpolation2d = parameter["Interpolation 2D"]
                layer.interpolation3d = parameter["Interpolation 3D"]
                layer.depiction = parameter["Depiction"]
                layer.iso_threshold = float(parameter["ISO Threshold"])
            
            else:
                layer: napari.layers.Layer = sv.create_layer_type(
                    viewer,
                    parameter["Layer Type"],
                    parameters_dict[
                        parameter["Acting On"]])
            
            layer.blending = parameter["Blending"]
            layer.opacity = float(parameter["Opacity"])
            center: tuple = (float(parameter["Center 0"]),
                             float(parameter["Center 1"]),
                             float(parameter["Center 2"]))
            angles: tuple = (float(parameter["Angle 0"]),
                             float(parameter["Angle 1"]),
                             float(parameter["Angle 2"]))
            orientation: tuple = (parameter["Orientation Depth"],
                                  parameter["Orientation Vert"],
                                  parameter["Orientation Horiz"])
            viewer.camera.center = center
            viewer.camera.zoom = float(parameter["Zoom"])
            viewer.camera.angles = angles
            viewer.camera.perspective = float(parameter["Perspective"])
            viewer.camera.orientation = orientation
            screenshot_array: np.ndarray = sv.get_screenshot(viewer)
            sv.close_viewer(viewer)  
            rw.write_im(
                screenshot_array,
                save_dir,
                f"{file_name}_screenshot_{screenshot_index}")
            screenshot_index += 1
            
        
        #########################
        # Manipulate Operations #
        #########################
        
        elif parameter["Name"].find("Trimmed") == 0:
            print("\nTrimming...")
            if parameter["X Bounds"].lower() == "true":
                x_bounds: list = [
                    int(parameter["X Min"]),
                    int(parameter["X Max"])]
            else:
                x_bounds: None = None
            if parameter["Y Bounds"].lower() == "true":
                y_bounds: list = [
                    int(parameter["Y Min"]),
                    int(parameter["Y Max"])]
            else:
                y_bounds: None = None
            if parameter["Z Bounds"].lower() == "true":
                z_bounds: list = [
                    int(parameter["Z Min"]),
                    int(parameter["Z Max"])]
            else:
                z_bounds: None = None
            if parameter["Bounds as Slices"].lower() == "true":
                bounds_as_slices: bool = True
            else:
                bounds_as_slices: bool = False
                
            bounds_dict = {"X": x_bounds, "Y": y_bounds, "Z": z_bounds}
            im_array = cc.trim(
                im_array,
                bounds_dict = bounds_dict,
                bounds_as_slices = bounds_as_slices,
                conserve_mem = True)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Padded") == 0:
            print("\nPadding...")
            if parameter["X Bounds"].lower() == "true":
                x_bounds: list = [
                    int(parameter["X Min"]),
                    int(parameter["X Max"])]
            else:
                x_bounds: None = None
            if parameter["Y Bounds"].lower() == "true":
                y_bounds: list = [
                    int(parameter["Y Min"]),
                    int(parameter["Y Max"])]
            else:
                y_bounds: None = None
            if parameter["Z Bounds"].lower() == "true":
                z_bounds: list = [
                    int(parameter["Z Min"]),
                    int(parameter["Z Max"])]
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
            im_array = cc.pad(
                im_array,
                bounds_dict = bounds_dict,
                bounds_as_slices = bounds_as_slices,
                padded_color = padded_color,
                conserve_mem = True)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Cropped") == 0:
            print("\nCropping...")
            if np.issubdtype(im_array.dtype, np.floating):
                mask_color: float = float(parameter["Masked Color"])
            else:
                mask_color: int = int(parameter["Masked Color"])
            
            mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
            im_array = cc.crop(
                im_array,
                mask_array,
                mask_color = mask_color,
                conserve_mem = True)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        elif parameter["Name"].find("Extend") == 0:
            print("\nExtending...")
            im_array = cc.project_mask(
                im_array,
                num_slices = int(parameter["Slice Count"]) - 1)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        
        ########################
        # Transform Operations #
        ########################
        
        elif parameter["Name"].find("Resliced") == 0:
            print("\nReslicing...")
            im_array = trans.reslice(
                im_array,
                parameter["Orientation"])
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Rotated") == 0:
            print("\nRotating...")
            if parameter["Resize"].lower() == "true":
                resize: bool = True
            else:
                resize: bool = False
            if parameter["Clockwise"].lower() == "true":
                im_array = trans.rotate(
                    im_array, float(
                        parameter["Angle"]),
                    "CW",
                    resize = resize)
            else:
                im_array = trans.rotate(
                    im_array,
                    float(
                        parameter["Angle"]),
                    resize = resize)
                
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Mirrored") == 0:
            print("\nMirroring...")
            im_array = trans.mirror(im_array, int(parameter["Direction"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        elif parameter["Name"].find("Resized") == 0:
            print("\nResizing...")
            if int(parameter["X Dim"]) == 0:
                x_dim: int = util.get_ax_str_dim(im_array, "x")
            else:
                x_dim: int = int(parameter["X Dim"])
            if int(parameter["Y Dim"]) == 0:
                y_dim: int = util.get_ax_str_dim(im_array, "y")
            else:
                y_dim: int = int(parameter["Y Dim"])
            if int(parameter["Z Dim"]) == 0:
                z_dim: int = util.get_ax_str_dim(im_array, "z")
            else:
                z_dim: int = int(parameter["Z Dim"])
            if util.is_3d_rgb["3D"]:
                dims: tuple = (z_dim, y_dim, x_dim)
            else:
                dims: tuple = (y_dim, x_dim)
                
            im_array = trans.resize(im_array, dims)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Rescaled") == 0:
            print("\nRescaling...")
            im_array = trans.rescale(im_array, float(parameter["Scale"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        
        ######################
        # Masking Operations #
        ######################
        
        elif parameter["Name"].find("Masked") == 0:
            print("\nMasking...")
            if np.issubdtype(im_array.dtype, np.floating):
                mask_color: float = float(parameter["Masked Color"])
            else:
                mask_color: int = int(parameter["Masked Color"])
                
            mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
            im_array = cc.mask(
                im_array,
                mask_array,
                method = parameter["Method"],
                mask_color = mask_color,
                conserve_mem = True)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        elif parameter["Name"].find("Mask Logic") == 0:
            print("\nLogic operation...")
            mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
            im_array = cc.mask_logic(
                im_array,
                mask_array,
                parameter["Method"])
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        
        ##########################
        # Pixel Value Operations #
        ##########################
        
        elif parameter["Name"].find("Converted") == 0:
            print("\nConverting type...")
            if parameter["Auto Normalize"].lower() == "true":
                auto_normalize: bool = True
            else:
                auto_normalize: bool = False
            if parameter["Bounds"].lower() == "true":
                im_array = pixels.convert_im_type(
                    im_array,
                    parameter["Type"],
                    norm = auto_normalize,
                    float_bounds = (
                        float(parameter["Min"]),
                        float(parameter["Max"])))
            else:
                im_array = pixels.convert_im_type(
                    im_array,
                    parameter["Type"],
                    norm = auto_normalize)
                
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Normalized") == 0:
            print("\nNormalizing...")
            if parameter["Input Range"].lower() == "true":
                in_range: tuple = (
                    float(parameter["Input Min"]),
                    float(parameter["Input Max"]))
            else:
                in_range: str = "image"
            if parameter["Output Range"].lower() == "true":
                out_range: tuple = (
                    float(parameter["Output Min"]),
                    float(parameter["Output Max"]))
            else:
                out_range: str = "dtype"
                
            im_array = pixels.normalize(
                im_array,
                in_range = in_range,
                out_range = out_range)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Saturated") == 0:
            print("\nSaturating...")
            if parameter["Auto Normalize"].lower() == "true":
                auto_normalize: bool = True
            else:
                auto_normalize: bool = False
            if parameter["Bounds as Percentages"].lower() == "true":
                bounds_as_percentages: bool = True
            else:
                bounds_as_percentages: bool = False
            if bounds_as_percentages and parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
                
            im_array = pixels.saturate(
                im_array,
                (
                    float(parameter["Min Bound"]),
                    float(parameter["Max Bound"])),
                auto_normalize = auto_normalize,
                bounds_as_percents = bounds_as_percentages,
                mask_array = mask_array)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Equalized") == 0:
            print("\nEqualizing...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
                
            im_array = pixels.equalize_histogram(
                im_array, parameter["Method"],
                mask_array = mask_array,
                radius = int(parameter["Local Radius"]),
                along_axis = along_axis,
                axis = int(parameter["Axis"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        elif parameter["Name"].find("Re-assigned") == 0:
            print("\nRe-assigning...")
            if parameter["All Except Input"].lower() == "true":
                im_array[im_array != float(parameter["Input Intensity"])] = float(
                    parameter["Output Intensity"])
            else:
                im_array[im_array == float(parameter["Input Intensity"])] = float(
                    parameter["Output Intensity"])
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        elif parameter["Name"].find("Grayscale") == 0:
            print("\nConverting to grayscale...")
            im_array = pixels.rgb_2_gray(im_array)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        elif parameter["Name"].find("Inverted") == 0:
            print("\nInverting...")
            im_array = pixels.invert(im_array)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        
        ########################
        # Denoising Operations #
        ########################
        
        elif parameter["Name"].find("Bilateral") == 0:
            print("\nBilateral filter...")
            if int(parameter["Window Size"]) == 0:
                win_size: None = None
            else:
                win_size: int = int(parameter["Window Size"])
            
            im_array = denoising.bilateral(
                im_array,
                axis = int(parameter["Axis"]),
                win_size = win_size,
                sigma_color = float(parameter["Sigma Color"]),
                sigma_spatial = float(parameter["Sigma Spatial"]),
                bins = int(parameter["Bins"]),
                mode = parameter["Mode"],
                cval = float(parameter["CVal"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Gaussian") == 0:
            print("\nGaussian blur...")
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
                
            im_array = denoising.gaussian(
                im_array,
                sigma = float(parameter["Sigma"]),
                truncate = float(parameter["Truncate"]),
                mode = parameter["Mode"],
                cval = float(parameter["CVal"]),
                axial = along_axis,
                axis = int(parameter["Axis"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Non-Local Means") == 0:
            print("\nNon-local means filter...")
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
                
            im_array = denoising.non_local_means(
                im_array,
                patch_size = int(parameter["Patch Size"]),
                patch_distance = int(parameter["Patch Distance"]),
                h = float(parameter["Cut Off Distance"]),
                sigma = float(parameter["Sigma"]),
                axial = along_axis,
                axis = int(parameter["Axis"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Removed Background") == 0:
            print("\nRemoving background...")
            im_array = denoising.remove_background(
                im_array,
                radius = int(parameter["Radius"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        elif parameter["Name"].find("Ring Removal") == 0:
            print("\nRemoving rings...")
            if parameter["Sorting"].lower() == "true":
                sorting: bool = True
            else:
                sorting: bool = False
                
            if parameter["Method"] == "FFT":
                im_array = fourier.fft_ring_removal(
                    im_array,
                    cutoff_freq = int(parameter["FFT Freq Cutoff"]),
                    filter_order = int(parameter["FFT Filter Order"]),
                    rows = int(parameter["FFT Rows"]),
                    sorting = sorting,
                    square_axis = int(parameter["Square Axis"]))
            
            elif parameter["Method"] == "Wavelet":
                im_array = fourier.wavelet_ring_removal(
                    im_array,
                    level = int(parameter["Wavelet Level"]),
                    size = int(parameter["Wavelet Damping Size"]),
                    wavelet = parameter["Wavelet"],
                    sorting = sorting,
                    square_axis = int(parameter["Square Axis"]))
                
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("TV Bregman") == 0:
            print("\nTV Bregman filter...")
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
            if parameter["Isotropic"].lower() == "true":
                isotropic: bool = True
            else:
                isotropic: bool = False
                
            im_array = denoising.tv_bregman(
                im_array,
                weight = float(parameter["Weight"]),
                eps = float(parameter["Epsilon"]),
                max_num_iter = int(parameter["Max Iterations"]),
                isotropic = isotropic,
                axial = along_axis,
                axis = int(parameter["Axis"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("TV Chambolle") == 0:
            print("\nTV Chambolle filter...")
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
                
            im_array = denoising.tv_chambolle(
                im_array,
                weight = float(parameter["Weight"]),
                eps = float(parameter["Epsilon"]),
                max_num_iter = int(parameter["Max Iterations"]),
                axial = along_axis,
                axis = int(parameter["Axis"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Wavelet") == 0:
            print("\nWavelet filter...")
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
            if parameter["Rescale Sigma"].lower() == "true":
                rescale_sigma: bool = True
            else:
                rescale_sigma: bool = False
            if float(parameter["Sigma"]) == 0:
                sigma: None = None
            else:
                sigma: float = float(parameter["Sigma"])
            if int(parameter["Wavelet Levels"]) == 0:
                wavelet_levels: None = None
            else:
                wavelet_levels: int = int(parameter["Wavelet Levels"])
                
            im_array = denoising.wavelet(
                im_array,
                wavelet = parameter["Wavelet"],
                mode = parameter["Mode"],
                sigma = sigma,
                wavelet_levels = wavelet_levels,
                rescale_sigma = rescale_sigma,
                method = parameter["Threshold Method"],
                axial = along_axis,
                axis = int(parameter["Axis"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        
        ###########################
        # Segmentation Operations #
        ###########################
        
        elif parameter["Name"].find("Manual Threshold") == 0:
            print("\nManual thresholding...")
            im_array = thresh.gui_threshold(
                im_array,
                (float(parameter["Min"]),
                 float(parameter["Max"])))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Histogram Threshold") == 0:
            print("\nHistogram thresholding...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
                
            im_array = thresh.hist(
                im_array,
                method = parameter["Method"],
                otsu_classes = int(parameter["Otsu Classes"]),
                mask_array = mask_array)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Local Threshold") == 0:
            print("\nLocal thresholding...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
            if float(parameter["Sigma Range"]) == 0:
                r: None = None
            else:
                r: float = float(parameter["Sigma Range"])
                
            im_array = thresh.local(
                im_array,
                mask_array = mask_array,
                method = parameter["Method"],
                radius = int(parameter["Radius"]),
                window_size = int(parameter["Radius"]),
                k = float(parameter["Sigma Weight"]),
                r = r)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Label Segmentation") == 0:
            print("\nConnectivity labeling...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array = parameters_dict[parameter["Mask Used"]]
            else:
                mask_array = None
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
                
            im_array = thresh.label(
                im_array,
                mask_array = mask_array,
                connectivity = int(parameter["Connectivity"]),
                background = float(parameter["Background"]),
                positional = along_axis,
                axis = int(parameter["Axis"]),
                randomize = False)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Watershed") == 0:
            print("\nWatershed labeling...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array = parameters_dict[parameter["Mask Used"]]
            else:
                mask_array = None
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
            
            im_array = detect.watershed(
                im_array,
                mask_array = mask_array,
                background = float(parameter["Background"]),
                connectivity = int(parameter["Connectivity"]),
                radius = int(parameter["Watershed Radius"]),
                compactness = float(parameter["Watershed Compactness"]),
                along_axis = along_axis,
                axis = int(parameter["Axis"]),
                randomize = False)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Random Walk") == 0:
            print("\nRandom walk thresholding...")
            im_array = detect.random_walk(
                im_array,
                (
                    float(parameter["Lower Percentile"]),
                    float(parameter["Upper Percentile"])),
                float(parameter["Beta"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Morph Snakes") == 0:
            print("\nMorphological snakes thresholding...")
            im_array = detect.morph_snakes(
                im_array,
                parameter["Method"],
                square_size = int(parameter["Square Size"]),
                num_iter = int(parameter["Iterations"]),
                smoothing = int(parameter["Smoothing"]),
                alpha = float(parameter["Alpha"]),
                sigma = float(parameter["Sigma"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        
        #########################
        # Morphology Operations #
        #########################
        
        elif parameter["Name"].find("Dilation") == 0:
            print("\nDilating...")
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
                
            im_array = morph.dilation(
                im_array,
                int(parameter["Iterations"]),
                along_axis = along_axis)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Erosion") == 0:
            print("\nEroding...")
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
                
            im_array = morph.erosion(
                im_array,
                int(parameter["Iterations"]),
                along_axis = along_axis)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Closing") == 0:
            print("\nClosing...")
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
            
            im_array = morph.closing(
                im_array,
                int(parameter["Dilations"]),
                int(parameter["Erosions"]),
                along_axis = along_axis)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Opening") == 0:
            print("\nOpening...")
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
            
            im_array = morph.opening(
                im_array,
                int(parameter["Erosions"]),
                int(parameter["Dilations"]),
                along_axis = along_axis)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Top Hat") == 0:
            print("\nTop hat...")
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
            
            im_array = morph.tophat(
                im_array,
                parameter["Method"],
                int(parameter["Dilations"]),
                int(parameter["Erosions"]),
                along_axis = along_axis)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        
        #####################
        # Filter Operations #
        #####################
        
        elif parameter["Name"].find("FFT") == 0:
            print("\nComputing FFT...")
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
                
            im_array = fourier.ft(im_array, along_axis)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        elif parameter["Name"].find("Remove Objects") == 0:
            print("\nRemoving objects...")
            if parameter["Along Axis"].lower() == "true":
                along_axis: bool = True
            else:
                along_axis: bool = False
                
            im_array = morph.remove_objects(
                im_array,
                float(parameter["Size Threshold"]),
                parameter["Method"],
                background = int(parameter["Background"]),
                pixel_size = float(parameter["Pixel Size"]),
                connectivity = int(parameter["Connectivity"]),
                along_axis = along_axis,
                axis = int(parameter["Axis"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Distance Transform") == 0:
            print("\nComputing distance transform...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
            if parameter["Round Values"].lower() == "true":
                round_values: bool = True
            else:
                round_values: bool = False
            if parameter["Mask Before DT"].lower() == "true":
                mask_before_dt: bool = True
            else:
                mask_before_dt: bool = False
                
            im_array = morph.distance_transform(
                im_array,
                float(parameter["Pixel Size"]),
                round_values = round_values,
                mask_array = mask_array,
                mask_before_dt = mask_before_dt)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        elif parameter["Name"].find("Max Inscribed Spheres") == 0:
            print("\nComputing max inscribed spheres...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
            if parameter["Smooth"].lower() == "true":
                smooth: bool = True
            else:
                smooth: bool = False
            if parameter["ImJ Approx"].lower() == "true":
                imj_approx: bool = True
            else:
                imj_approx: bool = False
            if parameter["Mask Before DT"].lower() == "true":
                mask_before_dt: bool = True
            else:
                mask_before_dt: bool = False
            if parameter["Return Diameter"].lower() == "true":
                return_diameter: bool = True
            else:
                return_diameter: bool = False
                
            im_array = morph.max_inscribed_spheres(
                im_array,
                parameter["Method"].lower(),
                float(parameter["Pixel Size"]),
                return_diameter = return_diameter,
                smooth = smooth,
                imj_approx = imj_approx,
                mask_array = mask_array,
                mask_before_dt = mask_before_dt,
                sizes = int(parameter["Sizes"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
            
        ######################
        # Feature Operations #
        ######################
        
        elif parameter["Name"].find("Edge Detection") == 0:
            print("\nDetecting edges...")
            if parameter["Slice Wise"].lower() == "true":
                slice_axis: int = int(parameter["Slice Axis"])
            else:
                slice_axis: None = None
            if parameter["Filter Along Axis"].lower() == "true":
                apply_axis: int = int(parameter["Apply Axis"])
            else:
                apply_axis: None = None
                
            im_array = detect.edge(
                im_array,
                method = parameter["Method"],
                sigma = float(parameter["Sigma"]),
                ksize = int(parameter["K Size"]),
                alpha = float(parameter["Alpha"]),
                igg_sigma = float(parameter["Sigma"]),
                slice_axis = slice_axis,
                apply_axis = apply_axis,
                edge_method = parameter["Edges Method"],
                cval = float(parameter["Constant Value"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        elif parameter["Name"].find("Corner Detection") == 0:
            print("\nDetecting corners...")
            if parameter["Correct Anomalies"].lower() == "true":
                correct_anomalies: bool = True
            else:
                correct_anomalies: bool = False
            
            im_array = detect.corners(
                im_array, parameter["Method"],
                n = int(parameter["Fast N"]),
                threshold = float(parameter["Fast Threshold"]),
                harris_method = parameter["Harris Method"],
                k = float(parameter["Harris K"]),
                eps = float(parameter["Harris Epsilon"]),
                sigma = float(parameter["Sigma"]),
                window_size = int(parameter["Window Size"]),
                correct_anomalies = correct_anomalies,
                return_mode = parameter["Return Mode"])
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        elif parameter["Name"].find("Ridge Detection") == 0:
            print("\nDetecting ridges...")
            if parameter["Black Ridges"].lower() == "true":
                black_ridges: bool = True
            else:
                black_ridges: bool = False
            if float(parameter["Gamma"]) == 0:
                gamma: None = None
            else:
                gamma: float = float(parameter["Gamma"])
                
            im_array = detect.ridges(
                im_array,
                method = parameter["Method"],
                scale_range = (
                    float(parameter["Scale Min"]),
                    float(parameter["Scale Max"])),
                scale_step = float(parameter["Scale Step"]),
                alpha = float(parameter["Alpha"]),
                beta = float(parameter["Beta"]),
                gamma = gamma,
                black_ridges = black_ridges,
                mode = parameter["Mode"],
                cval = float(parameter["Constant Value"]))
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        elif parameter["Name"].find("Blob Detection") == 0:
            print("\nDetecting blobs...")
            if float(parameter["Threshold_Rel"]) == 0:
                threshold_rel: None = None
            else:
                threshold_rel: float = float(parameter["Threshold_Rel"])
            if parameter["Exclude Border"].lower() == "true":
                exclude_border: bool = True
            else:
                exclude_border: bool = False
            if parameter["Log Scale"].lower() == "true":
                log_scale: bool = True
            else:
                log_scale: bool = False
                
            im_array = detect.blobs(
                im_array,
                method = parameter["Method"],
                min_sigma = int(parameter["Min Sigma"]),
                max_sigma = int(parameter["Max Sigma"]),
                sigma_ratio = float(parameter["Sigma Ratio"]),
                threshold = float(parameter["Threshold"]),
                overlap = float(parameter["Overlap"]),
                num_sigma = int(parameter["Num Sigma"]),
                threshold_rel = threshold_rel,
                exclude_border = exclude_border,
                log_scale = log_scale)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        elif parameter["Name"].find("Skeleton Detection") == 0:
            print("\nDetecting skeleton...")
            im_array = detect.skeleton(
                im_array,
                parameter["Method"])
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
        
        
        ##########################
        # Calculation Operations #
        ##########################
        
        elif parameter["Name"].find("Calculate Statistics") == 0:
            print("\nCalculating statistics...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
                
            stats_df: pd.DataFrame = quant.global_statistics(
                im_array,
                mask_array = mask_array,
                print_results = False)
            stats_df.insert(0, "File Name", file_name)
            save_path: str = save_dir + f"/Stats_{stats_index}.csv"
            
            if not os.path.isfile(save_path):
                stats_df.to_csv(
                    save_path,
                    header = "column_names",
                    index = False)
            else:
                stats_df.to_csv(
                    save_path,
                    mode = "a",
                    header = False,
                    index = False)
            stats_index += 1
        
        elif parameter["Name"].find("Calculate Bulk Value") == 0:
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
            if parameter["Include Background"].lower() == "true":
                include_background: bool = True
            else:
                include_background: bool = False
            if parameter["Normalize"].lower() == "true":
                auto_normalize: bool = True
            else:
                auto_normalize: bool = False
                
            if parameter["Quantity Measured"] == "Volume":
                print("\nMeasuring volume...")
                quantity_df: pd.DataFrame = quant.get_volume(
                    im_array,
                    mask_array = mask_array,
                    scale = float(parameter["Pixel Size"]),
                    units = parameter["Units"],
                    include_background = include_background,
                    background = float(parameter["Background"]),
                    normalize = auto_normalize,
                    print_results = False)
            
            elif parameter["Quantity Measured"] == "Area":
                print("\nMeasuring area...")
                quantity_df: pd.DataFrame = quant.get_area(
                    im_array,
                    mask_array = mask_array,
                    scale = float(parameter["Pixel Size"]),
                    units = parameter["Units"],
                    include_background = include_background,
                    background = float(parameter["Background"]),
                    normalize = auto_normalize,
                    print_results = False)
                
            elif parameter["Quantity Measured"] == "Length":
                print("\nMeasuring length...")
                quantity_df: pd.DataFrame = quant.get_length(
                    im_array,
                    mask_array = mask_array,
                    scale = float(parameter["Pixel Size"]),
                    units = parameter["Units"],
                    include_background = include_background,
                    background = float(parameter["Background"]),
                    normalize = auto_normalize,
                    print_results = False)
                
            quantity_df.insert(0, "File Name", file_name)
            quantity_df["Units"] = quantity_df.attrs["units"]
            save_path: str = save_dir + f"/Bulk_Value_{quantity_index}.csv"
            
            if not os.path.isfile(save_path):
                quantity_df.to_csv(
                    save_path,
                    header = "column_names",
                    index = False)
            else:
                quantity_df.to_csv(
                    save_path,
                    mode = "a",
                    header = False,
                    index = False)
            quantity_index += 1
        
        elif parameter["Name"].find("Calculate Surface Value") == 0:
            print("\nCalculating surface perimeter/area...")
            if parameter["Correct Overestimation"].lower() == "true":
                correct_overestimation: bool = True
            else:
                correct_overestimation: bool = False
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
                
            surf_df: pd.DataFrame = quant.get_surface_contact(
                im_array,
                float(parameter["Phase Intensity"]),
                mask_array = mask_array,
                pixel_size = float(parameter["Pixel Size"]),
                units = parameter["Units"],
                correct_overestimation = correct_overestimation,
                print_results = False)
            save_path: str = save_dir + f"/Surface_Value_{surf_index}.csv"
            surf_df.insert(0, "File Name", file_name)
            surf_df["Units"] = surf_df.attrs["units"]
            
            if not os.path.isfile(save_path):
                surf_df.to_csv(
                    save_path,
                    header = "column_names",
                    index = False)
            else:
                surf_df.to_csv(
                    save_path,
                    mode = "a",
                    header = False,
                    index = False)
            surf_index += 1
        
        elif parameter["Name"].find("Calculate Contact Value") == 0:
            print("\nCalculating contact value...")
            if parameter["Correct Overestimation"].lower() == "true":
                correct_overestimation: bool = True
            else:
                correct_overestimation: bool = False
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
                
            cont_df: pd.DataFrame = quant.get_surface_contact(
                im_array,
                (
                    float(parameter["Phase 1 Intensity"]),
                    float(parameter["Phase 2 Intensity"])),
                mask_array = mask_array,
                pixel_size = float(parameter["Pixel Size"]),
                units = parameter["Units"],
                correct_overestimation = correct_overestimation,
                print_results = False)
            save_path: str = save_dir + f"/Contact_Value_{cont_index}.csv"
            cont_df.insert(0, "File Name", file_name)
            cont_df["Units"] = cont_df.attrs["units"]
            
            if not os.path.isfile(save_path):
                cont_df.to_csv(
                    save_path,
                    header = "column_names",
                    index = False)
            else:
                cont_df.to_csv(
                    save_path,
                    mode = "a",
                    header = False,
                    index = False)
            cont_index += 1
            
        elif parameter["Name"].find("Calculate Specific Surface") == 0:
            print("\nCalculating specific surface...")
            if parameter["Correct Overestimation"].lower() == "true":
                correct_overestimation: bool = True
            else:
                correct_overestimation: bool = False
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
            
            spec_df: pd.DataFrame = quant.get_specific_surface(
                im_array,
                pixel_size = float(parameter["Pixel Size"]),
                units = parameter["Units"],
                bulk_method = parameter["Bulk Method"].lower(),
                correct_overestimation = correct_overestimation,
                print_results = False,
                mask_array = mask_array)
            save_path: str = save_dir + f"/Specific_Surface_{spec_index}.csv"
            spec_df.insert(0, "File Name", file_name)
            
            if not os.path.isfile(save_path):
                spec_df.to_csv(
                    save_path,
                    header = "column_names",
                    index = False)
            else:
                spec_df.to_csv(
                    save_path,
                    mode = "a",
                    header = False,
                    index = False)
            spec_index += 1
        
        elif parameter["Name"].find("Calculate Fractal Dimension") == 0:
            print("\nCalculating fractal dimension...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
                
            fractal_dim: np.float64 = quant.estimate_fractal_dimension(
                im_array,
                metric = parameter["Metric"].lower(),
                rescale_factor = float(parameter["Rescale Factor"]),
                print_results = False,
                mask_array = mask_array)
            fractal_df: pd.DataFrame = pd.DataFrame(
                {"Fractal Dimension": np.array([fractal_dim]),
                 "Rescale Factor": np.array([float(parameter["Rescale Factor"])])})
            save_path: str = save_dir + f"/Fractal_Dimension_{frac_index}.csv"
            fractal_df.insert(0, "File Name", file_name)
            
            if not os.path.isfile(save_path):
                fractal_df.to_csv(
                    save_path,
                    header = "column_names",
                    index = False)
            else:
                fractal_df.to_csv(
                    save_path,
                    mode = "a",
                    header = False,
                    index = False)
            frac_index += 1
            
        
        ###################
        # Plot Operations #
        ###################
        
        elif parameter["Name"].find("Histogram Plot") == 0:
            print("\nGenerating histogram...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
            if float(parameter["X Max"]) == 0:
                x_lims: None = None
            else:
                x_lims: tuple = (
                    float(parameter["X Min"]),
                    float(parameter["X Max"]))
            if float(parameter["Y Max"]) == 0:
                y_lims: None = None
            else:
                y_lims: tuple = (0, float(parameter["Y Max"]))
            if parameter["Remove Edges"].lower() == "true":
                ignore_edges: bool = True
            else:
                ignore_edges: bool = False
            if parameter["Normalize"].lower() == "true":
                normalize: bool = True
            else:
                normalize: bool = False
            if int(parameter["Num Bins"]) == 0:
                nbins: None = None
            else:
                nbins: int = int(parameter["Num Bins"])
                
            fig, hist_ax = plt.subplots(layout = "constrained")
            hist_ax: plt.Axes = plots.histogram_axis(
                im_array,
                hist_ax,
                x_label = "Gray Value",
                mask_array = mask_array,
                xlims = x_lims,
                ylims = y_lims,
                ignore_edges = ignore_edges,
                normalize = normalize,
                nbins = nbins)
            
            if parameter["Add CDF"].lower() == "true":
                cdf_ax: plt.Axes = hist_ax.twinx()
                cdf_ax = plots.cdf_axis(
                    im_array,
                    cdf_ax,
                    x_label = "Gray Value",
                    mask_array = mask_array,
                    xlims = x_lims)
                cdf_ax.set_ylabel(
                    "Probability",
                    rotation = 270,
                    va = "bottom")
                
            rw.write_plot(
                fig,
                f"{file_name}_histogram_{hist_index}",
                save_dir)
            plt.close(fig)
            hist_index += 1
        
        elif parameter["Name"].find("Gray Level Plot") == 0:
            print("\nGenerating gray levels plot...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
                
            fig = plots.gray_level(im_array, mask_array = mask_array)
            rw.write_plot(
                fig,
                f"{file_name}_gray_levels_{gray_index}",
                save_dir)
            plt.close(fig)
            gray_index += 1
        
        elif parameter["Name"].find("Axis Distribution Plot") == 0:
            print("\nGenerating axial distribution...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
            if float(parameter["X Max"]) == 0:
                x_lims: None = None
            else:
                x_lims: tuple = (
                    float(parameter["X Min"]),
                    float(parameter["X Max"]))
            if float(parameter["Y Max"]) == 0:
                y_lims: None = None
            else:
                y_lims: tuple = (0, float(parameter["Y Max"]))
            if parameter["Remove Edges"].lower() == "true":
                ignore_edges: bool = True
            else:
                ignore_edges: bool = False
            if parameter["Normalize"].lower() == "true":
                normalize: bool = True
            else:
                normalize: bool = False
            if parameter["Include Background"].lower() == "true":
                include_background: bool = True
            else:
                include_background: bool = False
            mode: str = "phase distrib"
            distrib_mode: str = parameter["Type"]
                
            if parameter["Time Series"].lower() == "true":
                mode: str = "time series"
                temporal_scale = parameter["Time Scale"]
                temporal_units = parameter["Time Units"]
            else:
                temporal_scale = None
                temporal_units = None
            
            fig, line_df = plots.line(
                im_array, mode,
                distrib_mode = distrib_mode,
                size_mode = parameter["Type"],
                pixel_size = float(parameter["Pixel Size"]),
                units = parameter["Units"],
                mask_array = mask_array,
                temporal_scale = temporal_scale,
                temporal_units = temporal_units,
                axis = int(parameter["Axis"]),
                include_background = include_background,
                background = float(parameter["Background"]),
                ignore_edges = ignore_edges,
                normalize = normalize,
                norm_method = parameter["Normalize Method"],
                xlims = x_lims,
                ylims = y_lims,
                return_df = True)
            rw.write_plot(
                fig,
                f"{file_name}_axial_distribution_{axis_dist_index}",
                save_dir)
            plt.close(fig)
            
            if parameter["Export Data"].lower() == "true":
                line_df.to_csv(
                    f"{save_dir}/{file_name}_axial_distribution_{axis_dist_index}.csv",
                    header = "column names",
                    index = False)
            axis_dist_index += 1
        
        elif parameter["Name"].find("Domain Size Distribution Plot") == 0:
            print("\nGenerating domain size distribution...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
            if float(parameter["X Max"]) == 0:
                x_lims: None = None
            else:
                x_lims: tuple = (
                    float(parameter["X Min"]),
                    float(parameter["X Max"]))
            if float(parameter["Y Max"]) == 0:
                y_lims: None = None
            else:
                y_lims: tuple = (0, float(parameter["Y Max"]))
            if parameter["Remove Edges"].lower() == "true":
                ignore_edges: bool = True
            else:
                ignore_edges: bool = False
            if parameter["Normalize"].lower() == "true":
                normalize: bool = True
            else:
                normalize: bool = False
            if int(parameter["Num Bins"]) == 0:
                nbins: None = None
            else:
                nbins: int = int(parameter["Num Bins"])
            if float(parameter["Max Bound"]) == 0:
                max_bound: None = None
            else:
                max_bound: float = float(parameter["Max Bound"])
            if parameter["Alternate X Label"].lower() == "true":
                x_label: str = parameter["X Label"]
            else:
                x_label: None = None
            
            fig, psd_df, hist_stats_df = plots.size_distribution(
                im_array,
                mode = parameter["Type"],
                diam_rad_mode = parameter["Diameter Radius Mode"],
                units = parameter["Units"],
                x_label = x_label,
                mask_array = mask_array,
                xlims = x_lims,
                ylims = y_lims,
                pixel_size = float(parameter["Pixel Size"]),
                normalize = normalize,
                ignore_edges = ignore_edges,
                background = float(parameter["Background"]),
                nbins = nbins,
                max_bound = max_bound,
                return_df = True)
            rw.write_plot(
                fig,
                f"{file_name}_size_distribution_{psd_index}",
                save_dir)
            plt.close(fig)
            
            if parameter["Export Data"].lower() == "true":
                psd_df.to_csv(
                    f"{save_dir}/{file_name}_size_distribution_{psd_index}.csv",
                    header = "column names",
                    index = False)
                hist_stats_df.to_csv(
                    f"{save_dir}/{file_name}_size_distribution_stats_{psd_index}.csv",
                    header = "column names",
                    index = False)
            psd_index += 1
        
        elif parameter["Name"].find("Heat Map") == 0:
            print("\nGenerating heat map...")
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
            if parameter["Alternate Colorbar Label"].lower() == "true":
                colorbar_label: str = parameter["Colorbar Label"]
            else:
                colorbar_label: None = None
            if parameter["Define Limits"].lower() == "true":
                clim: tuple = (
                    float(parameter["Min Value"]),
                    float(parameter["Max Value"]))
            else:
                clim: None = None
                
            if parameter["Return Array"].lower() == "true":
                fig, im_array = plots.heat_map(
                    im_array,
                    mode = parameter["Method"],
                    cmap = parameter["Color Map"],
                    clim = clim,
                    mask_array = mask_array,
                    pixel_size = float(parameter["Pixel Size"]),
                    units = parameter["Units"],
                    axis = int(parameter["Axis"]),
                    height_orientation = parameter["Height Direction"],
                    cbar_label = colorbar_label,
                    return_array = True)
                parameters_dict[parameter["Name"]] = im_array
                last_image_name: str = parameter["Name"]
            
            else:
                fig = plots.heat_map(
                    im_array,
                    mode = parameter["Method"],
                    cmap = parameter["Color Map"],
                    clim = clim,
                    mask_array = mask_array,
                    pixel_size = float(parameter["Pixel Size"]),
                    units = parameter["Units"],
                    axis = int(parameter["Axis"]),
                    height_orientation = parameter["Height Direction"],
                    cbar_label = colorbar_label)
                
            rw.write_plot(fig, f"{file_name}_heat_map_{heat_index}", save_dir)
            plt.close(fig)
            heat_index += 1
            
        elif parameter["Name"].find("Resolution Dependence") == 0:
            print("\nPlotting resolution dependence...")
            if parameter["Estimate Fractal"].lower() == "true":
                estimate_fractal: bool = True
            else:
                estimate_fractal: bool = False
            if parameter["Logspace Points"].lower() == "true":
                logspace_points: bool = True
            else:
                logspace_points: bool = False
            if float(parameter["Lower Bound"]) == 0 or float(parameter["Upper Bound"]) == 0: 
                bounds: None = None
            else:
                bounds: tuple = (float(parameter["Lower Bound"]), float(parameter["Upper Bound"]))
            if parameter["Correct Overestimation"].lower() == "true":
                correct_overestimation: bool = True
            else:
                correct_overestimation: bool = False
            if float(parameter["X Min"]) == 0:
                xlims: None = None
            else:
                xlims: tuple = (float(parameter["X Min"]), float(parameter["X Max"]))
            if float(parameter["Y Max"]) == 0:
                ylims: None = None
            else:
                ylims: tuple = (float(parameter["Y Min"]), float(parameter["Y Max"]))
            if parameter["Apply Mask"].lower() == "true":
                mask_array: np.ndarray = parameters_dict[
                    parameter["Mask Used"]]
            else:
                mask_array: None = None
                
            fig, res_dep_df = plots.resolution_dependence_plot(
                im_array,
                metric = parameter["Metric"].lower(),
                bulk_method = parameter["Bulk Method"].lower(),
                estimate_fractal = estimate_fractal,
                pixel_size = float(parameter["Pixel Size"]),
                units = parameter["Units"],
                bounds = bounds,
                num_points = int(parameter["Num Points"]),
                logspace_points = logspace_points,
                correct_overestimation = correct_overestimation,
                xlims = xlims,
                ylims = ylims,
                return_df = True,
                mask_array = mask_array)
            rw.write_plot(
                fig,
                f"{file_name}_resolution_dependence_plot_{res_index}",
                save_dir)
            plt.close(fig)
            
            if parameter["Export Data"].lower() == "true":
                res_dep_df.to_csv(
                    f"{save_dir}/{file_name}_resolution_dependence_plot_{res_index}.csv",
                    header = "column names",
                    index = False)
            res_index += 1
            
            
        ########################
        # Visualize Operations #
        ########################
        
        elif parameter["Name"].find("Labels to Image") == 0:
            print("\nConverting labels to image...")
            im_array = pixels.labels_2_rgb(im_array)
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
            
        elif parameter["Name"].find("Image to Labels") == 0:
            print("\nConverting image to labels...")
            if parameter["Axial Gradient"].lower() == "true":
                im_array = thresh.create_axial_labels(
                    im_array,
                    int(parameter["Gradient Axis"]))
                if parameter["Define Limits"].lower() == "true":
                    lab_limits: tuple = (
                        float(parameter["Min Value"]),
                        float(parameter["Max Value"]))
                else:
                    lab_limits: tuple = (
                        (np.min(im_array) * float(parameter["Pixel Scale"])),
                        (np.max(im_array) * float(parameter["Pixel Scale"])))
                cmap, cbar = util.get_colormap(
                    im_array,
                    lab_limits = lab_limits, 
                    cmap = parameter["Color Map"],
                    cbar_scale = float(parameter["Pixel Scale"]),
                    cbar_units = parameter["Units"],
                    cbar_label = parameter["Colorbar Label"])
            else:
                if len(np.unique(im_array)) > 2:
                    if parameter["Define Limits"].lower() == "true":
                        lab_limits: tuple = (
                            float(parameter["Min Value"]),
                            float(parameter["Max Value"])
                        )
                    else:
                        lab_limits: tuple = (
                            (np.min(im_array)),
                            (np.max(im_array))
                        )
                    im_array = thresh.create_intensity_labels(
                        im_array,
                        clims = lab_limits,
                        pixel_scale = float(parameter["Pixel Scale"])
                    )
                    cmap, cbar = util.get_colormap(
                        im_array,
                        lab_limits = lab_limits,
                        cmap = parameter["Color Map"],
                        cbar_scale = float(parameter["Pixel Scale"]),
                        cbar_units = parameter["Units"],
                        cbar_label = parameter["Colorbar Label"]
                    )
                else:
                    lab_array = np.zeros(im_array.shape, np.int32)
                    for index, intensity in enumerate(np.unique(im_array)):
                        lab_array[im_array == intensity] = index
                    if parameter["Define Limits"].lower() == "true":
                        lab_limits: tuple = (
                            float(parameter["Min Value"]),
                            float(parameter["Max Value"])
                        )
                    else:
                        lab_limits: tuple = (0, np.max(lab_array))
                        if lab_limits[1] == lab_limits[0]:
                            lab_limits = (0, 1)
                    im_array = np.copy(lab_array)
                    cmap, cbar = util.get_colormap(
                        im_array,
                        lab_limits = lab_limits,
                        cmap = parameter["Color Map"],
                        cbar_scale = float(parameter["Pixel Scale"]),
                        cbar_units = parameter["Units"],
                        cbar_label = parameter["Colorbar Label"]
                    )
                
            cmaps[parameter["Name"]] = cmap
            parameters_dict[parameter["Name"]] = im_array
            last_image_name: str = parameter["Name"]
    
    return parameters_dict[last_image_name]


# Main

def main(im_format: str = "Stacks",
         stack_format: str = "Multi-Page",
         export_images: bool = True,
         export_multi_page: bool = True,
         copy_parameters: bool = True) -> None:
    
    if stack_format == "Sequence":
        title: str = "Select image folder(s)"
        directories: bool = True
    else:
        title: str = "Select image file(s)"
        directories: bool = False
    
    im_list: list[str] = rw.get_paths(directories, title)
    parameters_path: str = rw.get_path(True, "Select parameters directory")
    parameters_dict: dict[str, list, np.ndarray] = rw.read_parameters_dir(
        parameters_path)
    save_dir: str = rw.get_path(
        True,
        "Select output directory",
        parameters_path[:parameters_path.rfind("/")])
    batch_start: float = timer()
    
    if copy_parameters:
        os.mkdir(save_dir + "/Parameters")
        shutil.copytree(
            parameters_path,
            save_dir + "/Parameters",
            dirs_exist_ok = True)
        
    for index, im_path in enumerate(im_list, 1):
        cur_start: float = timer()
        print(f"\nImporting dataset {index} of {len(im_list)}...")
        
        if rw.get_ext(im_path) == "directory":
            file_name: str = im_path[
                (im_path.rfind("/") + 1):]
        else:
            file_name: str = im_path[
                (im_path.rfind("/") + 1):im_path.rfind(".")]
        
        if im_format == "Stacks":
            im_array: np.ndarray = rw.read_stack(im_path)
        elif im_format == "Singles":
            im_array: np.ndarray = rw.read_im(im_path)
        
        save_name: str = f"{file_name}_PyDoug"
        im_array = apply_parameters(
            im_array,
            parameters_dict.copy(),
            save_name,
            save_dir)
        
        if export_images:
            if im_format == "Stacks":
                rw.write_stack(
                    im_array,
                    save_dir,
                    save_name,
                    multi_page = export_multi_page)
            elif im_format == "Singles":
                rw.write_im(im_array, save_dir, save_name)
                
        cur_end: float = timer()
        print(f"\nFinished processing dataset {index} of {len(im_list)} in {(cur_end - cur_start):.2f} s!")
            
    batch_end = timer()
    print(f"\nFinished batch processing in {(batch_end - batch_start):.2f} s!")
    

if __name__ == "__main__":
    main()
