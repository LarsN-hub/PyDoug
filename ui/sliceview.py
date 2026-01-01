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
    
def create_im_layer(im_array: np.array, viewer: napari.viewer, layer_name: str = "Image") -> napari.layers.Image:
    
    im_layer = viewer.add_image(im_array, name = layer_name)
    
    return im_layer

def close_layer(viewer: napari.viewer, layer_name: str) -> None:
    
    viewer.layers.remove(layer_name)

def launch_and_view(im_array: np.array, layer_name: str = "Image") -> (napari.viewer, napari.layers.Image):
    
    viewer: napari.viewer = create_viewer()
    
    return viewer, create_im_layer(im_array, viewer, layer_name)

def extract_im(im_layer: napari.layers.image) -> np.array:
    
    return im_layer.data

def get_layer(viewer: napari.viewer, layer_name: str = "Image") -> napari.layers:
    
    layers: napari.components.Layerlist = viewer.layers
    retrieved_layer = None
    
    for index, layer in enumerate(layers):
        
        if layer.name == layer_name:
            
            retrieved_layer = layers[index]
    
    return retrieved_layer
    
def create_shape_layer(viewer: napari.viewer) -> napari.layers.Shapes:
    
    return viewer.add_shapes()

def add_shape(viewer: napari.viewer, shape_type: str = "rectangle", *, base_layer_name: str = "Image") -> napari.layers.Shapes:
    
    valid_shapes: tuple = ("rectangle", "ellipse", "line")
    
    if any(x == shape_type for x in valid_shapes):
        
        im_array_shape: tuple = get_layer(viewer, base_layer_name).data.shape
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
            
            shape_dimensions: np.array = np.array([[initial_start, initial_start], [initial_end, initial_start], [initial_end, initial_end], [initial_start, initial_end]])
        
        elif shape_type == "line":
            
            shape_dimensions: np.array = np.array([[initial_start, initial_start], [initial_start, initial_end]])
        
        shape_layer = get_layer(viewer, "Shapes")
        
        if not shape_layer:
            
            shape_layer = create_shape_layer(viewer)

        shape_layer.add(shape_dimensions, shape_type = shape_type, edge_color = "red", edge_width = 2, face_color = "#ff000000")
        
        return shape_layer
            
    else:
        
        print("\nInvalid shape type!")
        
def extract_shapes(viewer: napari.viewer) -> dict[str, np.array]:
    
    shape_layer = get_layer(viewer, "Shapes")
    
    if shape_layer:
        
        shape_coords: list[np.array] = shape_layer.data
        shape_types: list[str] = shape_layer.shape_type
        shape_dict: dict = {}
        
        for index, shape in enumerate(shape_types):
            
            shape_dict[shape] = shape_coords[index]
            
        return shape_dict
    
    else:
        
        print("\nNo shapes layer detected!")


# Main

def main() -> napari.viewer:
    
    viewer = create_viewer()
    
    return viewer

if __name__ == "__main__":
    
    main()