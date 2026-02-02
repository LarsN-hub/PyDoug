"""
Module for PyDoug GUI
"""


# Imports

import magicclass.widgets as mcw
import sliceview as sv
import napari
import pixels
import trans

from magicgui import magicgui
from magicgui import widgets
from qtpy.QtCore import Qt


# Globals

parameters_log: list[dict[str, dict]] = []
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
    
    return widgets.Container(widgets = [header, container], labels = False)

def modify_funcgui(funcgui, title: str) -> widgets.Container:
    
    return collapsible_container(box_container(funcgui), title)

@magicgui(
    Orientation = {"choices": reslice_list},
    call_button = "Reslice")
def reslice_widget(
    Image: napari.layers.Image,
    Orientation: str = "Top") -> napari.layers.Image:
    
    parameters_log.append(
        {"Reslice": {"Orientation": Orientation}})
    
    return napari.layers.Image(trans.reslice(Image.data, Orientation.lower()), name = "Reslice")

@magicgui(
    Angle = {"widget_type": "FloatSlider", "max": 360},
    call_button = "Rotate")
def rotate_widget(
    Image: napari.layers.Image,
    Clockwise: bool = False,
    Resize: bool = False,
    Angle: float = 0) -> napari.layers.Image:
    
    parameters_log.append(
        {"Rotate": {"Clockwise": Clockwise,
                    "Resize": Resize,
                    "Angle": Angle}})
    
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
    
    parameters_log.append(
        {"Mirror": {"Axis": Axis}})
    
    return napari.layers.Image(trans.mirror(Image.data, Axis), name = "Mirror")

@magicgui(
    call_button = "Rescale Resolution")
def rescale_widget(
        Image: napari.layers.Image,
        Scale: float = 0.5) -> napari.layers.Image:
    
    parameters_log.append(
        {"Rescale": {"Scale": Scale}})
    
    return napari.layers.Image(trans.rescale(Image.data, Scale), name = "Rescale")

@magicgui(
    Type = {"choices": convert_type_list},
    call_button = "Convert Type")
def convert_type_widget(
        Image: napari.layers.Image,
        Type: str = "Uint8",
        Auto_Normalize: bool = False,
        Bounds: bool = False,
        Min: float = 0,
        Max: float = 0) -> napari.layers.Image:
    
    parameters_log.append(
        {"Convert Type": {"Type": Type,
                          "Auto Normalize": Auto_Normalize,
                          "Bounds": Bounds,
                          "Min": Min,
                          "Max": Max}})
    
    if Bounds:
        
        return napari.layers.Image(pixels.convert_im_type(Image.data, Type.lower(), norm = Auto_Normalize), name = Type)
    
    else:
        
        return napari.layers.Image(pixels.convert_im_type(Image.data, Type.lower(), norm = Auto_Normalize, float_bounds = (Min, Max)), name = Type)

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
    
    parameters_log.append(
        {"Normalize": {"Input Range": Input_Range,
                       "Output Range": Output_Range,
                       "Input Min": Input_Min,
                       "Input Max": Input_Max,
                       "Output Min": Output_Min,
                       "Output Max": Output_Max}})
    
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
    
    parameters_log.append(
        {"Saturate": {"Auto Normalize": Auto_Normalize,
                      "Bounds as Percentages": Bounds_as_Percentages,
                      "Min Bound": Min_Bound,
                      "Max Bound": Max_Bound}})
    
    return napari.layers.Image(pixels.saturate(Image.data, (Min_Bound, Max_Bound), auto_normalize = Auto_Normalize, bounds_as_percents = Bounds_as_Percentages), name = "Saturate")

@magicgui(Method = {"choices": equalize_list},
          call_button = "Equalize Histogram")
def equalize_widget(
        Image: napari.layers.Image,
        Method: str = "Global") -> napari.layers.Image:
    
    parameters_log.append(
        {"Equalize": {"Method": Method}})
    
    return napari.layers.Image(pixels.equalize_histogram(Image.data, Method.lower()), name = "Equalize")

@magicgui(
    call_button = "Invert Intensities")
def invert_widget(
        Image: napari.layers.Image) -> napari.layers.Image:
    
    parameters_log.append(
        {"Invert": {}})
    
    return napari.layers.Image(pixels.invert(Image.data), name = "Invert")


# Main

def main() -> None:
    
    viewer = sv.create_viewer()
    
    mod_reslice: widgets.Container = modify_funcgui(reslice_widget, "Reslice")
    mod_rotate: widgets.Container = modify_funcgui(rotate_widget, "Rotate")
    mod_mirror: widgets.Container = modify_funcgui(mirror_widget, "Mirror")
    mod_rescale: widgets.Container = modify_funcgui(rescale_widget, "Rescale")
    trans_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_reslice, mod_rotate, mod_mirror, mod_rescale],
        labels = False,
        layout = "vertical")
    viewer.window.add_dock_widget(trans_container, tabify = True, name = "Transformations")
    
    mod_convert_type: widgets.Container = modify_funcgui(convert_type_widget, "Convert Type")
    mod_normalize: widgets.Container = modify_funcgui(normalize_widget, "Normalize")
    mod_saturate: widgets.Container = modify_funcgui(saturate_widget, "Saturate")
    mod_equalize: widgets.Container = modify_funcgui(equalize_widget, "Equalize")
    mod_invert: widgets.Container = modify_funcgui(invert_widget, "Invert")
    pixels_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_convert_type, mod_normalize, mod_saturate, mod_equalize, mod_invert],
        labels = False,
        layout = "vertical")
    viewer.window.add_dock_widget(pixels_container, tabify = True, name = "Pixels")
    

if __name__ == "__main__":
    
    main()