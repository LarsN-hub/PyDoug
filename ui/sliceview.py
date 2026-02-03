"""
Module for rendering images
"""


# Imports

import pandas as pd
import numpy as np
import napari
import math

from skimage import draw


# Functions

def create_viewer() -> napari.viewer.Viewer:
    
    return napari.Viewer()

def close_viewer(viewer: napari.viewer.Viewer) -> None:
    
    viewer.close()
    
def create_im_layer(im_array: np.ndarray, viewer: napari.viewer.Viewer, layer_name: str = "Image") -> napari.layers.Image:
    
    return viewer.add_image(im_array, name = layer_name)

def close_layer(viewer: napari.viewer.Viewer, layer_name: str) -> None:
    
    viewer.layers.remove(layer_name)

def launch_and_view(im_array: np.ndarray, layer_name: str = "Image") -> napari.viewer.Viewer | napari.layers.Image:
    
    viewer: napari.viewer.Viewer = create_viewer()
    
    return viewer, create_im_layer(im_array, viewer, layer_name)

def extract_im(im_layer: napari.layers.image) -> np.array:
    
    return im_layer.data

def get_layer(viewer: napari.viewer.Viewer, layer_name: str = "Image") -> napari.layers.Layer:
    
    layers: napari.components.LayerList = viewer.layers
    retrieved_layer = None
    
    for index, layer in enumerate(layers):
        
        if layer.name == layer_name:
            
            retrieved_layer = layers[index]
            
            break
    
    return retrieved_layer

def get_im_layers(viewer: napari.viewer.Viewer) -> list[napari.layers.Image]:
    
    layers: napari.components.LayerList = viewer.layers
    layers_list = []
    
    for layer in layers:
        
        if isinstance(layer, napari.layers.Image):
            
            layers_list.append(layer)
            
    return layers_list

def get_top_im_layer(viewer: napari.viewer.Viewer) -> napari.layers.Image:
    
    layers_list: list[napari.layers.Image] = get_im_layers(viewer)
    
    return layers_list[-1]
    
def create_shape_layer(viewer: napari.viewer.Viewer) -> napari.layers.Shapes:
    
    return viewer.add_shapes()

def add_shape(viewer: napari.viewer.Viewer, shape_type: str = "rectangle", *, base_layer_name: str = "Image") -> napari.layers.Shapes:
    
    im_array_shape: tuple[int] = get_layer(viewer, base_layer_name).data.shape
    min_dim: int = min(im_array_shape[0:2])
        
    if im_array_shape:
            
        initial_start: int = math.floor(min_dim * 0.25)
        initial_end: int = math.ceil(min_dim * 0.75)     
        
    else:
            
        initial_start: int = 0
        initial_end: int = 100
            
    if shape_type == "rectangle":
            
        shape_dimensions: np.ndarray = np.array([[initial_start, initial_start], [initial_end, initial_end]])
        
    elif shape_type == "ellipse":
            
        shape_dimensions: np.ndarray = np.array([[initial_start, initial_start], [initial_end, initial_start], [initial_end, initial_end], [initial_start, initial_end]])
    
    elif shape_type == "line":
            
        shape_dimensions: np.ndarray = np.array([[initial_start, initial_start], [initial_start, initial_end]])
        
    shape_layer = get_layer(viewer, "Shapes")
        
    if not shape_layer:
            
        shape_layer = create_shape_layer(viewer)

    shape_layer.add(shape_dimensions, shape_type = shape_type, edge_color = "red", edge_width = max(im_array_shape) / 200, face_color = "#ff000000")
        
    return shape_layer
        
def extract_shapes(viewer: napari.viewer.Viewer) -> dict[str, np.ndarray]:
    
    shape_layer = get_layer(viewer, "Shapes")
    
    if shape_layer:
        
        shape_coords: list[np.ndarray] = shape_layer.data
        shape_types: list[str] = shape_layer.shape_type
        shape_dict: dict = {}
        
        for index, shape in enumerate(shape_types):
            
            shape_dict[shape] = shape_coords[index]
            
        return shape_dict
    
    else:
        
        print("\nNo shapes layer detected!")
        
def get_line_scan(viewer: napari.viewer.Viewer, slice_range: tuple | str | None = None, *, pixel_size: float | int = 1.0, units: str = "pix") -> pd.DataFrame:
    
    if units == "um":
        
        units = "\u00b5m"
    
    im_array: np.ndarray = get_top_im_layer(viewer).data
    line_coords: np.ndarray = np.astype(np.round(extract_shapes(viewer)["line"]), np.int64)
    
    if not slice_range and line_coords.shape[1] == 3:
        
        slice_range = (line_coords[0, 0], (line_coords[0, 0] + 1))
        
    elif not slice_range and line_coords.shape[1] == 2:
        
        slice_range = (0, im_array.shape[0])
        
    elif slice_range == "all":
        
        slice_range = (0, im_array.shape[0])
        
    if line_coords.shape[1] == 3:
        
        r_start: int = int(line_coords[0, 1])
        r_end: int = int(line_coords[1, 1])
        c_start: int = int(line_coords[0, 2])
        c_end: int = int(line_coords[1, 2])
        
    else:
        
        r_start: int = int(line_coords[0, 0])
        r_end: int = int(line_coords[1, 0])
        c_start: int = int(line_coords[0, 1])
        c_end: int = int(line_coords[1, 1])
        
    rr, cc = draw.line(r_start, c_start, r_end, c_end)
    ls_array: np.ndarray = np.expand_dims(np.arange(0, len(rr)), 1) * pixel_size
    columns = ["Position"]
        
    for slice_index in range(slice_range[0], slice_range[1]):
        
        ls_array = np.hstack((ls_array, np.expand_dims(im_array[slice_index, rr, cc], 1)))
        columns.append(str(slice_index))
    
    ls_df: pd.DataFrame = pd.DataFrame(ls_array, columns = columns)
    ls_df.attrs = {"pos_units": units}
    
    return ls_df
                 

# Main

def main(im_array: np.ndarray) -> napari.viewer.Viewer | napari.layers.Image:
    
    return launch_and_view(im_array)

if __name__ == "__main__":
    
    main()