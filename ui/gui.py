"""
Module for PyDoug GUI
"""


# Imports

import sliceview as sv
import napari
import trans

from magicgui import magicgui


# Globals

reslice_list: list[str] = ["Top", "Bottom", "Left", "Right", "Back"]
mirror_list: list[int] = [0, 1, 2]


# Functions

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


# Main

def main() -> None:
    
    viewer = sv.create_viewer()
    viewer.window.add_dock_widget(reslice_widget)
    viewer.window.add_dock_widget(rotate_widget)
    viewer.window.add_dock_widget(mirror_widget)

if __name__ == "__main__":
    
    main()