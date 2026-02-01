"""
Module for PyDoug GUI
"""


# Imports

import sliceview as sv
import napari
import pixels
import trans

from magicgui import magicgui
from magicgui import widgets
from qtpy.QtCore import Qt


# Globals

reslice_list: list[str] = ["Top", "Bottom", "Left", "Right", "Back"]
mirror_list: list[int] = [0, 1, 2]
convert_type_list: list[str] = ["Uint8", "Uint16", "Int16", "Float", "Float32", "Float64", "Bool"]
equalize_list: list[str] = ["Global", "Local", "Adaptive"]


# Functions

def box_container(container: widgets.Container) -> widgets.Container:
    
    container.native.setObjectName("my_container")
    container.native.setStyleSheet("""
                                   #my_container {
                                       border: 2px solid #888;
                                       border-radius: 6px;
                                       }
                                   """)
                                   
    return container

def container_title(funcgui, title: str) -> None:
    
    label = widgets.Label(value = title)
    label.native.setAlignment(Qt.AlignCenter)
    label.native.setStyleSheet("font-weight: bold; padding: 6px;")
    funcgui.insert(0, label)
    funcgui.native.layout().setAlignment(Qt.AlignCenter)
    
def collapsible_container(container: widgets.Container, title: str) -> widgets.Container:
    
    header = widgets.PushButton(text = f"▼ {title}")
    header.native.setStyleSheet("""
                                text-align: left;
                                font-weight: bold;
                                """)
                                
    container.visible = True
    
    def toggle() -> None:
        
        container.visible = not container.visible
        arrow = "▼" if container.visible else "▶"
        header.text = f"{arrow} {title}"
        
    header.clicked.connect(toggle)
    
    return widgets.Container(widgets = [header, container])

@magicgui(
    Orientation = {"choices": reslice_list},
    call_button = "Reslice")
def reslice_widget(
    Image: napari.layers.Image,
    Orientation: str = "Top") -> napari.layers.Image:
    
    return napari.layers.Image(trans.reslice(Image.data, Orientation.lower()), name = "Reslice")

@magicgui(
    Angle = {"widget_type": "FloatSlider", "max": 360},
    call_button = "Rotate")
def rotate_widget(
    Image: napari.layers.Image,
    Clockwise: bool = False,
    Resize: bool = False,
    Angle: float = 0) -> napari.layers.Image:
    
    if Clockwise:
        
        return napari.layers.Image(trans.rotate(Image.data, Angle, "CW", resize = Resize), name = "Rotate")
    
    else:
        
        return napari.layers.Image(trans.rotate(Image.data, Angle, resize = Resize), name = "Rotate")
    
@magicgui(
    Axis = {"choices": mirror_list},
    call_button = "Mirror")
def mirror_widget(
    Image: napari.layers.Image,
    Axis: int = 1) -> napari.layers.Image:
    
    return napari.layers.Image(trans.mirror(Image.data, Axis), name = "Mirror")

@magicgui(
    Type = {"choices": convert_type_list},
    call_button = "Convert Type")
def convert_type_widget(
        Image: napari.layers.Image,
        Normalize: bool = False,
        Bounds: bool = False,
        Min: float = 0,
        Max: float = 0,
        Type: str = "Uint8") -> napari.layers.Image:
    
    if Bounds:
        
        return napari.layers.Image(pixels.convert_im_type(Image.data, Type.lower(), norm = Normalize), name = Type)
    
    else:
        
        return napari.layers.Image(pixels.convert_im_type(Image.data, Type.lower(), norm = Normalize, float_bounds = (Min, Max)), name = Type)

@magicgui(
    call_button = "Normalize")
def normalize_widget(
        Image: napari.layers.Image,
        Input_Range: bool = False,
        Input_Min: float = 0,
        Input_Max: float = 0,
        Output_Range: bool = False,
        Output_Min: float = 0,
        Output_Max: float = 0,
        ) -> napari.layers.Image:
    
    if Input_Range and Output_Range:
        
        return napari.layers.Image(pixels.normalize(Image.data, in_range = (Input_Min, Input_Max), out_range = (Output_Min, Output_Max)), name = "Normalize")
    
    elif Input_Range and not Output_Range:
        
        return napari.layers.Image(pixels.normalize(Image.data, in_range = (Input_Min, Input_Max)), name = "Normalize")
    
    elif Output_Range and not Input_Range:
        
        return napari.layers.Image(pixels.normalize(Image.data, out_range = (Output_Min, Output_Max)), name = "Normalize")

@magicgui(
    call_button = "Saturate")
def saturate_widget(
        Image: napari.layers.Image,
        Auto_Normalize: bool = False,
        Bounds_as_Percentages: bool = True,
        Min_Bound: float = 0,
        Max_Bound: float = 100) -> napari.layers.Image:
    
    return napari.layers.Image(pixels.saturate(Image.data, (Min_Bound, Max_Bound), auto_normalize = Auto_Normalize, bounds_as_percents = Bounds_as_Percentages), name = "Saturate")

@magicgui(Method = {"choices": equalize_list},
          call_button = "Equalize Histogram")
def equalize_widget(
        Image: napari.layers.Image,
        Method: str = "Global") -> napari.layers.Image:
    
    return napari.layers.Image(pixels.equalize_histogram(Image.data, Method.lower()), name = "Equalize")

@magicgui(
    call_button = "Rescale Resolution")
def rescale_widget(
        Image: napari.layers.Image,
        Scale: float = 0.5) -> napari.layers.Image:
    
    return napari.layers.Image(pixels.rescale(Image.data, Scale), name = "Rescale")

@magicgui(
    call_button = "Invert Intensities")
def invert_widget(
        Image: napari.layers.Image) -> napari.layers.Image:
    
    return napari.layers.Image(pixels.invert(Image.data), name = "Invert")


# Main

def main() -> None:
    
    viewer = sv.create_viewer()
    
    box_reslice: widgets.Container = box_container(reslice_widget)
    box_rotate: widgets.Container = box_container(rotate_widget)
    box_mirror: widgets.Container = box_container(mirror_widget)
    trans_container: widgets.Container = widgets.Container(
        widgets = [box_reslice, box_rotate, box_mirror],
        labels = False,
        layout = "vertical")
    trans_container = box_container(trans_container)
    trans_container = collapsible_container(trans_container, "Transformations")
    viewer.window.add_dock_widget(trans_container)
    
    box_convert_type: widgets.Container = box_container(convert_type_widget)
    box_normalize: widgets.Container = box_container(normalize_widget)
    box_saturate: widgets.Container = box_container(saturate_widget)
    box_equalize: widgets.Container = box_container(equalize_widget)
    box_rescale: widgets.Container = box_container(rescale_widget)
    box_invert: widgets.Container = box_container(invert_widget)
    pixels_container: widgets.Container = widgets.Container(
        widgets = [box_convert_type, box_normalize, box_saturate, box_equalize, box_rescale, box_invert],
        labels = False,
        layout = "vertical")
    pixels_container = box_container(pixels_container)
    pixels_container = collapsible_container(pixels_container, "Pixels")
    viewer.window.add_dock_widget(pixels_container)

if __name__ == "__main__":
    
    main()