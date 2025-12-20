"""
Module for rendering images
"""

# Imports

import numpy as np
import napari


# Functions

def launch_viewer() -> napari.viewer:
    
    return napari.Viewer()

def close_viewer(viewer: napari.viewer) -> None:
    
    viewer.close()
    
def view_im(im_array: np.array, viewer: napari.viewer) -> napari.layers.image:
    
    im_layer = viewer.add_image(im_array)
    viewer.dims.order = (2, 0, 1)
    
    return im_layer

def extract_im(im_layer: napari.layers.image) -> np.array:
    
    return im_layer.data


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()