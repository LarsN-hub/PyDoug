"""
Module for generating plots to analyze images
"""

# Imports

import numpy as np
import quant

from matplotlib import pyplot as plt
from matplotlib import figure


# Functions

def histogram(im_array: np.ndarray, *, mask_array: np.ndarray = None, return_data: bool = False) -> figure.Figure | dict:
    
    hist_dict: dict[str, np.ndarray] = quant.get_histogram(im_array, mask_array = mask_array)
    fig: plt.figure = plt.figure(dpi = 300)
    fax: plt.axes = plt.axes()
    fax.figure = fig
    fax.set_xlabel("Intensity")
    fax.set_ylabel("Counts")
    plt.hist(hist_dict["bin centers"], hist_dict["bin centers"], weights = hist_dict["counts"], axes = fax)
    
    if return_data:
        
        hist_dict["plot"] = fig
        
        return hist_dict
    
    else:
        
        return fig

def cdf(im_array: np.ndarray, *, mask_array: np.ndarray = None, return_data: bool = False) -> figure.Figure | dict:
    
    cdf_dict: dict[str, np.ndarray] = quant.get_cdf(im_array, mask_array = mask_array)
    fig: plt.figure = plt.figure(dpi = 300)
    fax: plt.axes = plt.axes()
    fax.figure = fig
    fax.set_xlabel("Intensity")
    fax.set_ylabel("Probability")
    fax.set_ylim(0, 1)
    plt.plot(cdf_dict["bin_centers"], cdf_dict["cdf"], "red")
    
    if return_data:
        
        cdf_dict["plot"] = fig
        
        return cdf_dict
    
    else:
        
        return fig

def hist_and_cdf(im_array: np.ndarray, *, mask_array: np.ndarray = None, return_data: bool = False) -> figure.Figure:
    
    hist_dict: dict[str, np.ndarray] = quant.get_histogram(im_array, mask_array = mask_array)
    cdf_dict: dict[str, np.ndarray] = quant.get_cdf(im_array, mask_array = mask_array)
    fig: plt.figure = plt.figure(dpi = 300)
    fax: plt.axes = plt.axes()
    fax.figure = fig
    fax.set_xlabel("Intensity")
    fax.set_ylabel("Counts")
    plt.hist(hist_dict["bin centers"], hist_dict["bin centers"], weights = hist_dict["counts"], axes = fax)
    fax2 = fax.twinx()
    fax2.set_xlabel("Intensity")
    fax2.set_ylabel("Probability")
    fax2.set_ylim(0, 1)
    plt.plot(cdf_dict["bin_centers"], cdf_dict["cdf"], "red")
    
    if return_data:
        
        return {"plot": fig, "histogram": hist_dict, "cdf": cdf_dict}
    
    else:
        
        return fig


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()