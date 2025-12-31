"""
Module for rendering images
"""

# Imports

import numpy as np
import napari
import math


# Functions

def create_viewer() -> napari.viewer:
    
    return napari.Viewer()

def close_viewer(viewer: napari.viewer) -> None:
    
    viewer.close()
    
def create_im_layer(im_array: np.array, viewer: napari.viewer, layer_name: str = "Image") -> napari.layers.image:
    
    im_layer = viewer.add_image(im_array, name = layer_name)
    
    return im_layer

def close_layer(viewer: napari.viewer, layer_name: str) -> None:
    
    viewer.layers.remove(layer_name)

def launch_and_view(im_array: np.array, layer_name: str = "Image") -> (napari.viewer, napari.layers.image):
    
    viewer: napari.viewer = create_viewer()
    
    return viewer, create_im_layer(im_array, viewer, layer_name)

def extract_im(im_layer: napari.layers.image) -> np.array:
    
    return im_layer.data

def get_im_shape(viewer: napari.viewer, layer_name: str = "Image") -> tuple | None:
    
    layers: napari.components.Layerlist = viewer.layers
    im_array_shape: tuple = ()
    
    for index, layer in enumerate(layers):
        
        if layer.name == layer_name:
            
            im_array_shape = layer.data.shape
            
    if im_array_shape:
        
        return im_array_shape
    
    else:
        
        print("\nNo data in layer!")
        
        return None

def create_shape_layer(viewer: napari.viewer, shape_type: str = "rectangle", *, base_layer_name: str = "Image") -> None:
    
    valid_shapes: tuple = ("rectangle", "ellipse", "line")
    
    if any(x == shape_type for x in valid_shapes):
        
        im_array_shape: tuple = get_im_shape(viewer, base_layer_name)
        min_dim: int = min(im_array_shape[0:2])
        
        if im_array_shape:
            
            initial_start: int = math.floor(min_dim * 0.25)
            initial_end: int = math.ceil(min_dim * 0.75)     
        
        else:
            
            initial_start: int = 0
            initial_end: int = 100
            
        if shape_type == "rectangle":
            
            shape_dimensions: np.array = np.array([[initial_start, initial_start], [initial_end, initial_end]])
        
        elif shape_type == "ellipse":
            
            pass
        
        elif shape_type == "line":
            
            pass
        
        shape_layer = viewer.add_shapes()
        shape_layer.add(shape_dimensions, shape_type = shape_type, edge_color = "red", face_color = "red")
        
        return shape_layer
            
    else:
        
        print("\nInvalid shape type!")


# Main

def main() -> napari.viewer:
    
    viewer = create_viewer()
    
    return viewer

if __name__ == "__main__":
    
    main()