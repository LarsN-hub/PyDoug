"""
Module for generating plots to analyze images
"""

# Imports

import numpy as np
import quant

from matplotlib import pyplot as plt


# Functions

def set_intensity_axlims(axis: plt.Axes, data_type: np.dtype, y_or_x: str = "x", *, axlims: tuple = None) -> plt.Axes:
    
    if axlims:
        
        if y_or_x == "x":
            
            axis.set_xbound(min(axlims), max(axlims))
        
        elif y_or_x == "y":
            
            axis.set_ybound(min(axlims), max(axlims))
        
    else:
        
        if data_type == "uint8":
            
            if y_or_x == "x":
                
                axis.set_xlim(0, 255)
            
            elif y_or_x == "y":
                
                axis.set_ylim(0, 255)
        
        elif data_type == "uint16":
            
            if y_or_x == "x":
                
                axis.set_xlim(0, 65535)
            
            elif y_or_x == "y":
                
                axis.set_ylim(0, 65535)
                
    return axis

def histogram_axis(data: np.ndarray | dict, input_ax: plt.Axes, *, mask_array: np.ndarray = None, axlims: tuple = None, ignore_edges: bool = False) -> plt.Axes:
    
    if isinstance(data, np.ndarray):
    
        hist_dict: dict[str, np.ndarray] = quant.get_histogram(data, mask_array = mask_array)
        
    else:
        
        hist_dict: dict[str, np.ndarray] = data.copy()
        
    if ignore_edges:
        
        hist_dict["bin centers"] = hist_dict["bin centers"][1:-1]
        hist_dict["counts"] = hist_dict["counts"][1:-1]
        
    hist_axis: plt.Axes = input_ax
    hist_axis.set_xlabel("Gray Value")
    hist_axis.set_ylabel("Counts")
    hist_axis.hist(hist_dict["bin centers"], hist_dict["bin centers"], weights = hist_dict["counts"])
    
    if axlims:
        
        hist_axis = set_intensity_axlims(hist_axis, hist_dict["bin centers"].dtype, "x", axlims = axlims)
        
    else:
        
        hist_axis.set_xbound(np.min(hist_dict["bin centers"]), np.max(hist_dict["bin centers"]))
        
    return hist_axis

def cdf_axis(data: np.ndarray | dict, input_ax: plt.Axes, *, mask_array: np.ndarray = None, axlims: tuple = None) -> plt.Axes:
    
    if isinstance(data, np.ndarray):
    
        cdf_dict: dict[str, np.ndarray] = quant.get_cdf(data, mask_array = mask_array)
        
    else:
        
        cdf_dict: dict[str, np.ndarray] = data.copy()
        
    cdf_axis: plt.Axes = input_ax
    cdf_axis.set_xlabel("Gray Value")
    cdf_axis.set_ylabel("Probability", rotation = 270, va = "bottom")
    cdf_axis.set_ylim(0, 1)
    cdf_axis.plot(cdf_dict["bin centers"], cdf_dict["cdf"], "red")
    
    if axlims:
        
        cdf_axis = set_intensity_axlims(cdf_axis, cdf_dict["bin centers"].dtype, "x", axlims = axlims)
        
    else:
        
        cdf_axis.set_xbound(np.min(cdf_dict["bin centers"]), np.max(cdf_dict["bin centers"]))
        
    return cdf_axis

def histogram(data: np.ndarray | dict, *, input_ax: plt.Axes = None, mask_array: np.ndarray = None, axlims: tuple = None, ignore_edges: bool = False) -> plt.Figure:
    
    fig, hist_ax = plt.subplots()
    hist_ax = histogram_axis(data, hist_ax, mask_array = mask_array, axlims = axlims, ignore_edges = ignore_edges)
    
    return fig

def cdf(data: np.ndarray | dict, *, input_ax: plt.Axes = None, mask_array: np.ndarray = None, axlims: tuple = None) -> plt.Figure:
    
    fig, cdf_ax = plt.subplots()
    cdf_ax = cdf_axis(data, cdf_ax, mask_array = mask_array, axlims = axlims)
    
    return fig

def hist_cdf(data: np.ndarray | dict, *, input_ax: plt.Axes = None, mask_array: np.ndarray = None, axlims: tuple = None, ignore_edges: bool = False) -> plt.Figure:
    
    fig, hist_ax = plt.subplots()
    hist_ax = histogram_axis(data, hist_ax, mask_array = mask_array, axlims = axlims, ignore_edges = ignore_edges)
    cdf_ax: plt.Axes = hist_ax.twinx()
    cdf_ax = cdf_axis(data, cdf_ax, mask_array = mask_array, axlims = axlims)
    
    return fig

def subplot_layout(num_plots: int) -> tuple:
    
    if num_plots == 1:
        
        return (1, 1)
    
    elif num_plots == 2:
        
        return (1, 2)
    
    elif num_plots == 3:
        
        return (1, 3)
    
    elif num_plots == 4:
        
        return (2, 2)
    
    elif num_plots == 5 or num_plots == 6:
        
        return (2, 3)
    
    elif num_plots == 7 or num_plots == 8 or num_plots == 9:
        
        return (3, 3)

def multi_plot(data_array: np.ndarray, function_list: list, layout: tuple = None) -> plt.Figure:
    
    functions: dict = {"hist": histogram_axis, "cdf": cdf_axis, "hist cdf": "hist cdf"}
       
    if not layout:
        
        layout: tuple = subplot_layout(len(data_array))
    
    fig, axs = plt.subplots(layout[0], layout[1])
    
    if any(x == "hist cdf" for x in function_list):
        
        cdf_axs = np.copy(axs)
    
    for index, data in enumerate(data_array):
        
        if functions[function_list[index]] == "hist cdf":
            
            axs[index] = histogram_axis(data, axs[index])
            cdf_axs[index]: plt.Axes = axs[index].twinx()
            cdf_axs[index] = cdf_axis(data, cdf_axs[index])
        
        else:
        
            functions[function_list[index]](data, input_ax = axs[index])
        
    fig.tight_layout()
    
    return fig
        
    
# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()    