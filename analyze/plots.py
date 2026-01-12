"""
Module for generating plots to analyze images
"""

# Imports

import numpy as np

from matplotlib import pyplot as plt
from skimage import exposure


# Functions

def histogram(im_array: np.array, *, mask_array: np.array = None) -> plt.figure:
    
    if np.any(mask_array):
    
        counts, bin_centers = exposure.histogram(im_array[mask_array])
        
    else:
        
        counts, bin_centers = exposure.histogram(im_array)
    
    fig: plt.figure = plt.figure(dpi = 300)
    fax: plt.axes = plt.axes()
    fax.figure = fig
    fax.set_xlabel("Intensity")
    fax.set_ylabel("Counts")
    plt.hist(bin_centers, bin_centers, weights = counts, axes = fax)
    
    return fig

def cdf(im_array: np.array, *, mask_array: np.array = None) -> plt.figure:
    
    if np.any(mask_array):
    
        im_cdf, bin_centers = exposure.cumulative_distribution(im_array[mask_array])
        
    else:
        
        im_cdf, bin_centers = exposure.cumulative_distribution(im_array)
        
    fig: plt.figure = plt.figure(dpi = 300)
    fax: plt.axes = plt.axes()
    fax.figure = fig
    fax.set_xlabel("Intensity")
    fax.set_ylabel("Probability")
    fax.set_ylim(0, 1)
    plt.plot(bin_centers, im_cdf, "red")
    
    return fig

def hist_and_cdf(im_array: np.array, *, mask_array: np.array = None) -> plt.figure:
    
    if np.any(mask_array):
    
        counts, hist_bin_centers = exposure.histogram(im_array[mask_array])
        im_cdf, cdf_bin_centers = exposure.cumulative_distribution(im_array[mask_array])
        
    else:
        
        counts, hist_bin_centers = exposure.histogram(im_array)
        im_cdf, cdf_bin_centers = exposure.cumulative_distribution(im_array)
        
    fig: plt.figure = plt.figure(dpi = 300)
    fax: plt.axes = plt.axes()
    fax.figure = fig
    fax.set_xlabel("Intensity")
    fax.set_ylabel("Counts")
    plt.hist(hist_bin_centers, hist_bin_centers, weights = counts, axes = fax)
    fax2 = fax.twinx()
    fax2.set_xlabel("Intensity")
    fax2.set_ylabel("Probability")
    fax2.set_ylim(0, 1)
    plt.plot(cdf_bin_centers, im_cdf, "red")


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()