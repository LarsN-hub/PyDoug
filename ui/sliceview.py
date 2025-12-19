"""
Module for rendering images
"""

# Imports

import numpy as np
import napari


# Functions

def launch_napari() -> napari.viewer:
    
    viewer = napari.Viewer()
    
    return viewer

def close_napari(viewer: napari.viewer) -> None:
    
    viewer.close()
    
def view_im(im_array: np.array, viewer: napari.viewer) -> napari.layers.image:
    
    im_layer: napari.layers.image = viewer.add_image(im_array)
    
    return im_layer


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()