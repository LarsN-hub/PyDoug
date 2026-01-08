"""
Module for generating plots to analyze images
"""

# Imports

import numpy as np

from matplotlib import pyplot as plt
from skimage import exposure


# Functions

def histogram(im_array: np.array) -> plt.figure:
    
    counts, bin_centers = exposure.histogram(im_array)
    fig: plt.figure = plt.figure(dpi = 300)
    fax: plt.axes = plt.axes()
    fax.figure = fig
    fax.set_xlabel("Intensity")
    fax.set_ylabel("Counts")
    plt.hist(bin_centers, bin_centers, weights = counts, axes = fax)
    
    return fig


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()