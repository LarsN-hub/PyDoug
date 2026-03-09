"""
Module for batch processing of images from pre-made parameters
"""


# Imports

import pandas as pd
import numpy as np
import shutil
import os

from matplotlib import pyplot as plt

from PyDoug.ui import readwrite as rw
from PyDoug.proc import cropclip as cc, denoising, detect, fourier, morph, pixels, thresh, trans, util
from PyDoug.analyze import quant, plots


# Functions

def apply_parameters(im_array: np.ndarray,
                     parameters_dict: dict[str, list, np.ndarray],
                     file_name: str = None,
                     save_dir: str = None) -> np.ndarray:
    
    parameters_log: list[dict] = parameters_dict["Parameters"]
    stats_index: int = 0
    vol_area_index: int = 0
    surf_index: int = 0
    cont_index: int = 0
    hist_index: int = 0
    gray_index: int = 0
    axis_dist_index: int = 0
    psd_index: int = 0
    heat_index: int = 0
    
    for parameter in parameters_log:
        
        #########################
        # Manipulate Operations #
        #########################
        
        if parameter["Name"].find("Trimmed") == 0:
            
            print("\nTrimming...")
            
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
            
            print("\nPadding...")
            
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
        
        elif parameter["Name"].find("Cropped") == 0:
            
            print("\nCropping...")
            
            if np.issubdtype(im_array.dtype, np.floating):
                
                mask_color: float = float(parameter["Masked Color"])
                
            else:
                
                mask_color: int = int(parameter["Masked Color"])
            
            mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
            im_array = cc.crop(im_array, mask_array,
                               mask_color = mask_color,
                               conserve_mem = True)
            
        elif parameter["Name"].find("Extend") == 0:
            
            print("\nExtending...")
            
            im_array = cc.project_mask(im_array, num_slices = int(parameter["Slice Count"]) - 1)
            
        
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
            im_array = cc.mask(im_array, mask_array,
                               method = parameter["Method"],
                               mask_color = mask_color,
                               conserve_mem = True)
        
        
        ########################
        # Transform Operations #
        ########################
        
        elif parameter["Name"].find("Resliced") == 0:
            
            print("\nReslicing...")
            im_array = trans.reslice(im_array, parameter["Orientation"])
        
        elif parameter["Name"].find("Rotated") == 0:
            
            print("\nRotating...")
            
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
            
            print("\nMirroring...")
            im_array = trans.mirror(im_array, int(parameter["Direction"]))
        
        elif parameter["Name"].find("Rescaled") == 0:
            
            print("\nRescaling...")
            im_array = trans.rescale(im_array, float(parameter["Scale"]))
        
        
        ###########################
        # Pixel Values Operations #
        ###########################
        
        elif parameter["Name"].find("Converted") == 0:
            
            print("\nConverting type...")
            
            if parameter["Auto Normalize"].lower() == "true":
                
                auto_normalize: bool = True
                
            else:
                
                auto_normalize: bool = False
                
            if parameter["Bounds"].lower() == "true":
                
                im_array = pixels.convert_im_type(im_array,
                                                  parameter["Type"],
                                                  norm = auto_normalize,
                                                  float_bounds = (float(parameter["Min"]), float(parameter["Max"])))
                
            else:
                
                im_array = pixels.convert_im_type(im_array,
                                                  parameter["Type"],
                                                  norm = auto_normalize)
        
        elif parameter["Name"].find("Normalized") == 0:
            
            print("\nNormalizing...")
            
            if parameter["Input Range"].lower() == "true":
                
                in_range: tuple = (float(parameter["Input Min"]), float(parameter["Input Max"]))
                
            else:
                
                in_range: str = "image"
                
            if parameter["Output Range"].lower() == "true":
                
                out_range: tuple = (float(parameter["Output Min"]), float(parameter["Output Max"]))
                
            else:
                
                out_range: str = "dtype"
                
            im_array = pixels.normalize(im_array,
                                        in_range = in_range,
                                        out_range = out_range)
        
        elif parameter["Name"].find("Saturated") == 0:
            
            print("\nSaturating...")
            
            if parameter["Auto Normalize"].lower() == "true":
                
                auto_normalize: bool = True
                
            else:
                
                auto_normalize: bool = False
                
            im_array = pixels.saturate(im_array,
                                       (float(parameter["Min Bound"]), float(parameter["Max Bound"])),
                                       auto_normalize = auto_normalize)
        
        elif parameter["Name"].find("Equalized") == 0:
            
            print("\nEqualizing...")
            
            if parameter["Apply Mask"].lower() == "true":
                
                mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
                
            else:
                
                mask_array: None = None
                
            if parameter["Along Axis"].lower() == "true":
                
                along_axis: bool = True
                
            else:
                
                along_axis: bool = False
                
            im_array = pixels.equalize_histogram(im_array, parameter["Method"],
                                                 mask_array = mask_array,
                                                 radius = int(parameter["Local Radius"]),
                                                 along_axis = along_axis,
                                                 axis = int(parameter["Axis"]))
        
        elif parameter["Name"].find("Inverted") == 0:
            
            print("\nInverting...")
            im_array = pixels.invert(im_array)
        
        elif parameter["Name"].find("Re-assigned") == 0:
            
            print("\nRe-assigning...")
            im_array[im_array == float(parameter["Input Intensity"])] = float(parameter["Output Intensity"])
            
        elif parameter["Name"].find("Grayscale") == 0:
            
            print("\nConverting to grayscale...")
            im_array = pixels.rgb_2_gray(im_array)
        
        
        ########################
        # Denoising Operations #
        ########################
        
        elif parameter["Name"].find("Bilateral") == 0:
            
            print("\nBilateral filter...")
            
            if int(parameter["Window Size"]) == 0:
                
                win_size: None = None
                
            else:
                
                win_size: int = int(parameter["Window Size"])
            
            im_array = denoising.bilateral(im_array,
                                           axis = int(parameter["Axis"]),
                                           win_size = win_size,
                                           sigma_color = float(parameter["Sigma Color"]),
                                           sigma_spatial = float(parameter["Sigma Spatial"]),
                                           bins = int(parameter["Bins"]),
                                           mode = parameter["Mode"],
                                           cval = float(parameter["CVal"]))
        
        elif parameter["Name"].find("Gaussian") == 0:
            
            print("\nGaussian blur...")
            
            if parameter["Along Axis"].lower() == "true":
                
                along_axis: bool = True
                
            else:
                
                along_axis: bool = False
                
            im_array = denoising.gaussian(im_array,
                                          sigma = float(parameter["Sigma"]),
                                          truncate = float(parameter["Truncate"]),
                                          mode = parameter["Mode"],
                                          cval = float(parameter["CVal"]),
                                          axial = along_axis,
                                          axis = int(parameter["Axis"]))
        
        elif parameter["Name"].find("Non-Local Means") == 0:
            
            print("\nNon-local means filter...")
            
            if parameter["Along Axis"].lower() == "true":
                
                along_axis: bool = True
                
            else:
                
                along_axis: bool = False
                
            im_array = denoising.non_local_means(im_array,
                                                 patch_size = int(parameter["Patch Size"]),
                                                 patch_distance = int(parameter["Patch Distance"]),
                                                 h = float(parameter["Cut Off Distance"]),
                                                 sigma = float(parameter["Sigma"]),
                                                 axial = along_axis,
                                                 axis = int(parameter["Axis"]))
        
        elif parameter["Name"].find("Removed Background") == 0:
            
            print("\nRemoving background...")
            im_array = denoising.remove_background(im_array,
                                                   radius = int(parameter["Radius"]))
            
        elif parameter["Name"].find("Ring Removal") == 0:
            
            print("\nRemoving rings...")
            
            if parameter["Sorting"].lower() == "true":
                
                sorting: bool = True
                
            else:
                
                sorting: bool = False
                
            if parameter["Method"] == "FFT":
                
                im_array = fourier.fft_ring_removal(im_array,
                                                    cutoff_freq = int(parameter["FFT Freq Cutoff"]),
                                                    filter_order = int(parameter["FFT Filter Order"]),
                                                    rows = int(parameter["FFT Rows"]),
                                                    sorting = sorting,
                                                    square_axis = int(parameter["Square Axis"]))
            
            elif parameter["Method"] == "Wavelet":
                
                im_array = fourier.wavelet_ring_removal(im_array,
                                                        level = int(parameter["Wavelet Level"]),
                                                        size = int(parameter["Wavelet Damping Size"]),
                                                        wavelet = parameter["Wavelet"],
                                                        sorting = sorting,
                                                        square_axis = int(parameter["Square Axis"]))
        
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
                
            im_array = denoising.tv_bregman(im_array,
                                            weight = float(parameter["Weight"]),
                                            eps = float(parameter["Epsilon"]),
                                            max_num_iter = int(parameter["Max Iterations"]),
                                            isotropic = isotropic,
                                            axial = along_axis,
                                            axis = int(parameter["Axis"]))
        
        elif parameter["Name"].find("TV Chambolle") == 0:
            
            print("\nTV Chambolle filter...")
            
            if parameter["Along Axis"].lower() == "true":
                
                along_axis: bool = True
                
            else:
                
                along_axis: bool = False
                
            im_array = denoising.tv_chambolle(im_array,
                                              weight = float(parameter["Weight"]),
                                              eps = float(parameter["Epsilon"]),
                                              max_num_iter = int(parameter["Max Iterations"]),
                                              axial = along_axis,
                                              axis = int(parameter["Axis"]))
        
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
                
            im_array = denoising.wavelet(im_array,
                                         wavelet = parameter["Wavelet"],
                                         mode = parameter["Mode"],
                                         sigma = sigma,
                                         wavelet_levels = wavelet_levels,
                                         rescale_sigma = rescale_sigma,
                                         method = parameter["Threshold Method"],
                                         axial = along_axis,
                                         axis = int(parameter["Axis"]))
        
        
        ###########################
        # Segmentation Operations #
        ###########################
        
        elif parameter["Name"].find("Manual Threshold") == 0:
            
            print("\nManual thresholding...")
            im_array = thresh.gui_threshold(im_array,
                                            (float(parameter["Min"]), float(parameter["Max"])))
        
        elif parameter["Name"].find("Histogram Threshold") == 0:
            
            print("\nHistogram thresholding...")
            
            if parameter["Apply Mask"].lower() == "true":
                
                mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
                
            else:
                
                mask_array: None = None
                
            im_array = thresh.hist(im_array,
                                   method = parameter["Method"],
                                   otsu_classes = int(parameter["Otsu Classes"]),
                                   mask_array = mask_array)
        
        elif parameter["Name"].find("Local Threshold") == 0:
            
            print("\nLocal thresholding...")
            
            if parameter["Apply Mask"].lower() == "true":
                
                mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
                
            else:
                
                mask_array: None = None
                
            if float(parameter["Sigma Range"]) == 0:
                
                r: None = None
                
            else:
                
                r: float = float(parameter["Sigma Range"])
                
            im_array = thresh.local(im_array,
                                    mask_array = mask_array,
                                    method = parameter["Method"],
                                    radius = int(parameter["Radius"]),
                                    window_size = int(parameter["Radius"]),
                                    k = float(parameter["Sigma Weight"]),
                                    r = r)
        
        elif parameter["Name"].find("Label") == 0:
            
            print("\nConnectivity labelling...")
            
            if parameter["Apply Mask"].lower() == "true":
                
                mask_array = parameters_dict[parameter["Mask Used"]]
                
            else:
                
                mask_array = None
                
            if parameter["Along Axis"].lower() == "true":
                
                along_axis: bool = True
                
            else:
                
                along_axis: bool = False
                
            im_array = thresh.label(im_array,
                                    mask_array = mask_array,
                                    connectivity = int(parameter["Connectivity"]),
                                    background = float(parameter["Background"]),
                                    positional = along_axis,
                                    axis = int(parameter["Axis"]))
        
        elif parameter["Name"].find("Watershed") == 0:
            
            print("\nWatershed labelling...")
            
            if parameter["Apply Mask"].lower() == "true":
                
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
                                        radius = int(parameter["Watershed Radius"]),
                                        compactness = float(parameter["Watershed Compactness"]),
                                        along_axis = along_axis,
                                        axis = int(parameter["Axis"]))
        
        elif parameter["Name"].find("Random Walk") == 0:
            
            print("\nRandom walk thresholding...")
            im_array = detect.random_walk(im_array,
                                          (float(parameter["Lower Percentile"]), float(parameter["Upper Percentile"])),
                                          float(parameter["Beta"]))
        
        elif parameter["Name"].find("Morph Snakes") == 0:
            
            print("\nMorphological snakes thresholding...")
            im_array = detect.morph_snakes(im_array, parameter["Method"],
                                           square_size = int(parameter["Square Size"]),
                                           num_iter = int(parameter["Iterations"]),
                                           smoothing = int(parameter["Smoothing"]),
                                           alpha = float(parameter["Alpha"]),
                                           sigma = float(parameter["Sigma"]))
        
        
        #########################
        # Morphology Operations #
        #########################
        
        elif parameter["Name"].find("Remove Objects") == 0:
            
            print("\nRemoving objects...")
            
            if parameter["Along Axis"].lower() == "true":
                
                along_axis: bool = True
                
            else:
                
                along_axis: bool = False
                
            im_array = morph.remove_objects(im_array, float(parameter["Size Threshold"]),
                                            parameter["Method"],
                                            background = int(parameter["Background"]),
                                            pixel_size = float(parameter["Pixel Size"]),
                                            connectivity = int(parameter["Connectivity"]),
                                            along_axis = along_axis,
                                            axis = int(parameter["Axis"]))
        
        elif parameter["Name"].find("Dilation") == 0:
            
            print("\nDilating...")
            
            if parameter["Along Axis"].lower() == "true":
                
                along_axis: bool = True
                
            else:
                
                along_axis: bool = False
                
            im_array = morph.dilation(im_array, int(parameter["Iterations"]),
                                      along_axis = along_axis)
        
        elif parameter["Name"].find("Erosion") == 0:
            
            print("\nEroding...")
            
            if parameter["Along Axis"].lower() == "true":
                
                along_axis: bool = True
                
            else:
                
                along_axis: bool = False
                
            im_array = morph.erosion(im_array, int(parameter["Iterations"]),
                                     along_axis = along_axis)
        
        elif parameter["Name"].find("Closing") == 0:
            
            print("\nClosing...")
            
            if parameter["Along Axis"].lower() == "true":
                
                along_axis: bool = True
                
            else:
                
                along_axis: bool = False
            
            im_array = morph.closing(im_array,
                                     int(parameter["Dilations"]),
                                     int(parameter["Erosions"]),
                                     along_axis = along_axis)
        
        elif parameter["Name"].find("Opening") == 0:
            
            print("\nOpening...")
            
            if parameter["Along Axis"].lower() == "true":
                
                along_axis: bool = True
                
            else:
                
                along_axis: bool = False
            
            im_array = morph.opening(im_array,
                                     int(parameter["Erosions"]),
                                     int(parameter["Dilations"]),
                                     along_axis = along_axis)
        
        elif parameter["Name"].find("Top Hat") == 0:
            
            print("\nTop hat...")
            
            if parameter["Along Axis"].lower() == "true":
                
                along_axis: bool = True
                
            else:
                
                along_axis: bool = False
            
            im_array = morph.tophat(im_array,
                                    parameter["Method"],
                                    int(parameter["Dilations"]),
                                    int(parameter["Erosions"]),
                                    along_axis = along_axis)
            
            
        ######################
        # Feature Operations #
        ######################
        
        elif parameter["Name"].find("Edge Detection") == 0:
            
            print("\nDetecting edges...")
            
            if parameter["Along Axis"].lower() == "true":
                
                axis: int = int(parameter["Axis"])
                
            else:
                
                axis: None = None
                
            im_array = detect.edge(im_array,
                                   method = parameter["Method"],
                                   sigma = float(parameter["Sigma"]),
                                   ksize = int(parameter["K Size"]),
                                   alpha = float(parameter["Alpha"]),
                                   igg_sigma = float(parameter["Sigma"]),
                                   axis = axis)
        
        elif parameter["Name"].find("Corner Detection") == 0:
            
            print("\nDetecting corners...")
            
            if parameter["Correct Anomalies"].lower() == "true":
                
                correct_anomalies: bool = True
                
            else:
                
                correct_anomalies: bool = False
            
            im_array = detect.corners(im_array, parameter["Method"],
                                      n = int(parameter["Fast N"]),
                                      threshold = float(parameter["Fast Threshold"]),
                                      harris_method = parameter["Harris Method"],
                                      k = float(parameter["Harris K"]),
                                      eps = float(parameter["Harris Epsilon"]),
                                      sigma = float(parameter["Sigma"]),
                                      window_size = int(parameter["Window Size"]),
                                      correct_anomalies = correct_anomalies,
                                      return_mode = parameter["Return Mode"])
            
        elif parameter["Name"].find("Angle Measurement") == 0:
            
            print("\nMeasuring angles...")
            im_array = detect.opening_angles(im_array, int(parameter["Minimum Size"]))
        
        
        #######################
        # Analysis Operations #
        #######################
        
        elif parameter["Name"].find("Histogram Plot") == 0:
            
            print("\nGenerating histogram...")
            
            if parameter["Apply Mask"].lower() == "true":
                
                mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
                
            else:
                
                mask_array: None = None
                
            if float(parameter["X Max"]) == 0:
                
                x_lims: None = None
                
            else:
                
                x_lims: tuple = (float(parameter["X Min"]), float(parameter["X Max"]))
                
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
                
            fig, hist_ax = plt.subplots()
            hist_ax: plt.Axes = plots.histogram_axis(im_array, hist_ax,
                                                     x_label = "Gray Value",
                                                     mask_array = mask_array,
                                                     xlims = x_lims,
                                                     ylims = y_lims,
                                                     ignore_edges = ignore_edges,
                                                     normalize = normalize,
                                                     nbins = nbins)
            
            if parameter["Add CDF"].lower() == "true":
                
                cdf_ax: plt.Axes = hist_ax.twinx()
                cdf_ax = plots.cdf_axis(im_array, cdf_ax,
                                        x_label = "Gray Value",
                                        mask_array = mask_array,
                                        xlims = x_lims)
                cdf_ax.set_ylabel("Probability", rotation = 270, va = "bottom")
                
            rw.write_plot(fig, f"{file_name}_histogram_{hist_index}", save_dir)
            hist_index += 1
        
        elif parameter["Name"].find("Gray Level Plot") == 0:
            
            print("\nGenerating gray levels plot...")
            
            if parameter["Apply Mask"].lower() == "true":
                
                mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
                
            else:
                
                mask_array: None = None
                
            fig = plots.gray_level(im_array, mask_array = mask_array)
            rw.write_plot(fig, f"{file_name}_gray_levels_{gray_index}", save_dir)
            gray_index += 1
            
        elif parameter["Name"].find("FFT") == 0:
            
            print("\nComputing FFT...")
            
            if parameter["Along Axis"].lower() == "true":
                
                along_axis: bool = True
                
            else:
                
                along_axis: bool = False
                
            im_array = fourier.ft(im_array, along_axis)
        
        elif parameter["Name"].find("Misc Calculations") == 0:
            
            if parameter["Apply Mask"].lower() == "true":
                
                mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
                
            else:
                
                mask_array: None = None
            
            if parameter["Method"] == "Stats":
            
                print("\nCalculating statistics...")
                stats_df: pd.DataFrame = quant.global_statistics(im_array, mask_array = mask_array)
                stats_df.insert(0, "File Name", file_name)
                save_path: str = save_dir + f"/Stats_{stats_index}.csv"
                
                if not os.path.isfile(save_path):
                    
                    stats_df.to_csv(save_path, header = "column_names", index = False)
                    
                else:
                    
                    stats_df.to_csv(save_path, mode = "a", header = False, index = False)
                    
                stats_index += 1
                
            elif parameter["Method"] == "Percent Intensities":
                
                print("\nCalculating percentage intensities...")
                _ = quant.get_percent_intensities(im_array,
                                                  percentages = (float(parameter["Min Percent"]), float(parameter["Max Percent"])),
                                                  mask_array = mask_array)
                
            elif parameter["Method"] == "Volume/Area":
                
                print("\nCalculating volume/area...")
                
                if parameter["Include Background"].lower() == "true":
                    
                    include_background: bool = True
                    
                else:
                    
                    include_background: bool = False
                    
                if parameter["Normalize"].lower() == "true":
                    
                    auto_normalize: bool = True
                
                else:
                    
                    auto_normalize: bool = False
                
                if util.is_3d_rgb(im_array)["3D"]:
                    
                    vol_area_df: pd.DataFrame = quant.get_volume(im_array,
                                                                 mask_array = mask_array,
                                                                 scale = float(parameter["Pixel Size"]),
                                                                 units = parameter["Units"],
                                                                 include_background = include_background,
                                                                 background = float(parameter["Background"]),
                                                                 normalize = auto_normalize)
                
                else:
                    
                    vol_area_df: pd.DataFrame = quant.get_area(im_array,
                                                               mask_array = mask_array,
                                                               scale = float(parameter["Pixel Size"]),
                                                               units = parameter["Units"],
                                                               include_background = include_background,
                                                               background = float(parameter["Background"]),
                                                               normalize = auto_normalize)
                    
                vol_area_df.insert(0, "File Name", file_name)
                vol_area_df["Units"] = vol_area_df.attrs["units"]
                save_path: str = save_dir + f"/Volume_Area_{vol_area_index}.csv"
                
                if not os.path.isfile(save_path):
                    
                    vol_area_df.to_csv(save_path, header = "column_names", index = False)
                    
                else:
                    
                    vol_area_df.to_csv(save_path, mode = "a", header = False, index = False)
                    
                vol_area_index += 1
                
            elif parameter["Method"] == "Surface Perimeter/Area":
                
                print("\nCalculating surface perimeter/area...")
                surf_df: pd.DataFrame = quant.get_surface_contact(im_array,
                                                                  float(parameter["Surface Phase"]),
                                                                  mask_array = mask_array,
                                                                  pixel_size = float(parameter["Pixel Size"]),
                                                                  units = parameter["Units"])
                save_path: str = save_dir + f"/Surface_Area_{surf_index}.csv"
                surf_df.insert(0, "File Name", file_name)
                surf_df["Units"] = surf_df.attrs["units"]
                
                if not os.path.isfile(save_path):
                    
                    surf_df.to_csv(save_path, header = "column_names", index = False)
                    
                else:
                    
                    surf_df.to_csv(save_path, mode = "a", header = False, index = False)
                    
                surf_index += 1
                
            elif parameter["Method"] == "Contact Perimeter/Area":
                
                print("\nCalculating contact perimeter/area...")
                cont_df: pd.DataFrame = quant.get_surface_contact(im_array,
                                                                  (float(parameter["Contact Phase 1"]), float(parameter["Contact Phase 2"])),
                                                                  mask_array = mask_array,
                                                                  pixel_size = float(parameter["Pixel Size"]),
                                                                  units = parameter["Units"])
                save_path: str = save_dir + f"/Contact_Area_{cont_index}.csv"
                cont_df.insert(0, "File Name", file_name)
                cont_df["Units"] = cont_df.attrs["units"]
                
                if not os.path.isfile(save_path):
                    
                    cont_df.to_csv(save_path, header = "column_names", index = False)
                    
                else:
                    
                    cont_df.to_csv(save_path, mode = "a", header = False, index = False)
                    
                cont_index += 1
        
        elif parameter["Name"].find("Axis Distribution Plot") == 0:
            
            print("\nGenerating axial distribution...")
            
            if parameter["Apply Mask"].lower() == "true":
                
                mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
                
            else:
                
                mask_array: None = None
                
            if float(parameter["X Max"]) == 0:
                
                x_lims: None = None
                
            else:
                
                x_lims: tuple = (float(parameter["X Min"]), float(parameter["X Max"]))
                
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
                
            if parameter["Domain Size"].lower() == "false":
                
                mode: str = "phase distrib"
                
            else:
                
                mode: str = "psd distrib"
                
            distrib_mode: str = parameter["Type"]
                
            if parameter["Time Series"].lower() == "true":
                
                mode: str = "time series"
                temporal_scale = parameter["Time Scale"]
                temporal_units = parameter["Time Units"]
                
                if parameter["Domain Size"].lower() == "true":
                    
                    distrib_mode: str = "size"
                    
            else:
                
                temporal_scale = None
                temporal_units = None
            
            fig = plots.line(im_array, mode,
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
                             connectivity = int(parameter["Connectivity"]),
                             ignore_edges = ignore_edges,
                             normalize = normalize,
                             xlims = x_lims,
                             ylims = y_lims)
            rw.write_plot(fig, f"{file_name}_axial_distribution_{axis_dist_index}", save_dir)
            axis_dist_index += 1
        
        elif parameter["Name"].find("Domain Size Distribution Plot") == 0:
            
            print("\nGenerating domain size distribution...")
            
            if parameter["Apply Mask"].lower() == "true":
                
                mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
                
            else:
                
                mask_array: None = None
                
            if float(parameter["X Max"]) == 0:
                
                x_lims: None = None
                
            else:
                
                x_lims: tuple = (float(parameter["X Min"]), float(parameter["X Max"]))
                
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
            
            fig = plots.size_distribution(im_array,
                                          mode = parameter["Type"],
                                          units = parameter["Units"],
                                          mask_array = mask_array,
                                          xlims = x_lims,
                                          ylims = y_lims,
                                          pixel_size = float(parameter["Pixel Size"]),
                                          normalize = normalize,
                                          ignore_edges = ignore_edges,
                                          connectivity = int(parameter["Connectivity"]),
                                          background = float(parameter["Background"]),
                                          nbins = nbins,
                                          max_bound = max_bound)
            rw.write_plot(fig, f"{file_name}_size_distribution_{psd_index}", save_dir)
            psd_index += 1
        
        elif parameter["Name"].find("Heat Map") == 0:
            
            print("\nGenerating heat map...")
            
            if parameter["Apply Mask"].lower() == "true":
                
                mask_array: np.ndarray = parameters_dict[parameter["Mask Used"]]
                
            else:
                
                mask_array: None = None
            
            if parameter["Alternate Colorbar Label"].lower() == "true":
                
                colorbar_label: str = parameter["Colorbar Label"]
                
            else:
                
                colorbar_label: None = None
                
            if parameter["Define Limits"].lower() == "true":
                
                clim: tuple = (float(parameter["Min Value"]), float(parameter["Max Value"]))
                
            else:
                
                clim: None = None
                
            fig = plots.heat_map(im_array,
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
            heat_index += 1
        
    
    return im_array


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
        
        if im_format == "Stacks":
            
            im_array: np.ndarray = rw.read_stack(im_path)
        
        elif im_format == "Singles":
            
            im_array: np.ndarray = rw.read_im(im_path)
            
        im_array = apply_parameters(im_array, parameters_dict, file_name, save_dir)
        
        if export_images:
        
            if im_format == "Stacks":
                
                rw.write_stack(im_array, save_dir, file_name, multi_page = export_multi_page)
            
            elif im_format == "Singles":
                
                rw.write_im(im_array, save_dir, file_name)
            
    print("\nFinished batch processing!")
    

if __name__ == "__main__":
    
    main()