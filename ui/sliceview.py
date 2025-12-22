"""
Module for rendering images
"""

# Imports

import numpy as np
import napari


# Functions

def create_viewer() -> napari.viewer:
    
    return napari.Viewer()

def close_viewer(viewer: napari.viewer) -> None:
    
    viewer.close()
    
def create_layer(im_array: np.array, viewer: napari.viewer, layer_name: str = "im_array") -> napari.layers.image:
    
    im_layer = viewer.add_image(im_array, name = layer_name)
    viewer.dims.order = (2, 0, 1)
    
    return im_layer

def close_layer(viewer: napari.viewer, layer_name: str) -> None:
    
    viewer.layers.remove(layer_name)

def launch_and_view(im_array: np.array, layer_name: str = "im_array") -> napari.layers.image:
    
    viewer: napari.viewer = create_viewer()
    
    return viewer, create_layer(im_array, viewer, layer_name)

def extract_im(im_layer: napari.layers.image) -> np.array:
    
    return im_layer.data


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()