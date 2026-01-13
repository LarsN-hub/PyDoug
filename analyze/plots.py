"""
Module for generating plots to analyze images
"""

# Imports

import numpy as np
import quant

from matplotlib import pyplot as plt
from matplotlib import figure as fig
from matplotlib import axes as ax


# Functions

def set_intensity_axlims(axis: ax.Axes, data_type: np.dtype, y_or_x: str = "x", *, axlims: tuple = None) -> ax.Axes:
    
    if axlims:
        
        if y_or_x == "x":
            
            axis.set_xbound(min(axlims), max(axlims))
        
        elif y_or_x == "y":
            
            axis.set_ybound(min(axlims), max(axlims))
        
    else:
        
        if data_type == "uint8":
            
            if y_or_x == "x":
                
                axis.set_xbound(0, 255)
            
            elif y_or_x == "y":
                
                axis.set_ybound(0, 255)
        
        elif data_type == "uint16":
            
            if y_or_x == "x":
                
                axis.set_xbound(0, 65535)
            
            elif y_or_x == "y":
                
                axis.set_ybound(0, 65535)

def histogram(im_array: np.ndarray, *, mask_array: np.ndarray = None, return_data: bool = False, axlims: tuple = None) -> fig.Figure | dict:
    
    hist_dict: dict[str, np.ndarray] = quant.get_histogram(im_array, mask_array = mask_array)
    f: fig.Figure = plt.figure(dpi = 300)
    fax: ax.Axes = plt.axes()
    fax.figure = f
    fax.set_xlabel("Intensity")
    fax.set_ylabel("Counts")
    plt.hist(hist_dict["bin centers"], hist_dict["bin centers"], weights = hist_dict["counts"], axes = fax)
    
    if axlims:
        
        fax = set_intensity_axlims(fax, im_array.dtype, "x", axlims = axlims)
        
    else:
        
        fax.set_xbound(np.min(im_array), np.max(im_array))
    
    if return_data:
        
        hist_dict["plot"] = f
        
        return hist_dict
    
    else:
        
        return f

def cdf(im_array: np.ndarray, *, mask_array: np.ndarray = None, return_data: bool = False, axlims: tuple = None) -> fig.Figure | dict:
    
    cdf_dict: dict[str, np.ndarray] = quant.get_cdf(im_array, mask_array = mask_array)
    f: fig.Figure = plt.figure(dpi = 300)
    fax: ax.Axes = plt.axes()
    fax.figure = f
    fax.set_xlabel("Intensity")
    fax.set_ylabel("Probability")
    fax.set_ylim(0, 1)
    plt.plot(cdf_dict["bin centers"], cdf_dict["cdf"], "red")
    
    if axlims:
        
        fax = set_intensity_axlims(fax, im_array.dtype, "x", axlims = axlims)
        
    else:
        
        fax.set_xbound(np.min(im_array), np.max(im_array))
    
    if return_data:
        
        cdf_dict["plot"] = f
        
        return cdf_dict
    
    else:
        
        return f

def hist_and_cdf(im_array: np.ndarray, *, mask_array: np.ndarray = None, return_data: bool = False, axlims: tuple = None) -> fig.Figure | dict:
    
    hist_dict: dict[str, np.ndarray] = quant.get_histogram(im_array, mask_array = mask_array)
    cdf_dict: dict[str, np.ndarray] = quant.get_cdf(im_array, mask_array = mask_array)
    f: fig.Figure = plt.figure(dpi = 300)
    fax: ax.Axes = plt.axes()
    fax.figure = f
    fax.set_xlabel("Intensity")
    fax.set_ylabel("Counts")
    plt.hist(hist_dict["bin centers"], hist_dict["bin centers"], weights = hist_dict["counts"], axes = fax)
    fax2 = fax.twinx()
    fax2.set_xlabel("Intensity")
    fax2.set_ylabel("Probability", rotation = 270, va = "bottom")
    fax2.set_ylim(0, 1)
    plt.plot(cdf_dict["bin centers"], cdf_dict["cdf"], "red")
    
    if axlims:
        
        fax = set_intensity_axlims(fax, im_array.dtype, "x", axlims = axlims)
        
    else:
        
        fax.set_xbound(np.min(im_array), np.max(im_array))
    
    if return_data:
        
        return {"plot": f, "histogram": hist_dict, "cdf": cdf_dict}
    
    else:
        
        return f


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()