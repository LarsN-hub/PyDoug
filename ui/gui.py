"""
Module for PyDoug GUI
"""


# Imports

import magicclass.widgets as mcw
import readwrite as rw
import pathlib
import napari
import pixels
import trans

from qtpy.QtWidgets import QTabWidget
from magicclass import magicclass
from magicgui import magicgui
from magicgui import widgets
from qtpy.QtCore import Qt


# Globals

parameters_log: list[dict[str, dict]] = []
export_list: list[str] = ["Tiff", "HDF5"]
reslice_list: list[str] = ["Top", "Bottom", "Left", "Right", "Back"]
mirror_list: list[int] = [0, 1, 2]
convert_type_list: list[str] = ["Uint8", "Uint16", "Int16", "Float", "Float32", "Float64", "Bool"]
equalize_list: list[str] = ["Global", "Local", "Adaptive"]


# Classes

@magicclass
class ImageProcessor:
    
    def __init__(self, viewer: napari.viewer.Viewer) -> None:
        
        self.viewer: napari.viewer.Viewer = viewer
        self.viewer.layers.events.inserted.connect(self._on_layer_added)
        self.funcguis: dict[str, widgets.FunctionGui] = get_funcguis(ImageProcessor)
        
    def _on_layer_added(self, event):
        
        layer = event.value
        
        if isinstance(layer, napari.layers.Image):
            
            for func_name in self.funcguis:
                
                funcgui: widgets.FunctionGui = getattr(self, func_name)
                
                if hasattr(funcgui, "Image"):
                
                    funcgui.Image.reset_choices()
                    funcgui.Image.value = layer
                
                
    # I/O Widgets
    
    @magicgui(
        call_button = "Import Image")
    def im_import_widget(self,
        Multi_Page: bool = True,
        File_Path: pathlib.Path = pathlib.Path("~")) -> None:
        
        if Multi_Page:
            
            self.viewer.add_image(rw.read_stack(str(File_Path)), name = "Image")
            
        else:
            
            self.viewer.add_image(rw.read_im(str(File_Path)), name = "Image")
    
    @magicgui(
        Directory_Path = {"mode": "d"},
        call_button = "Import Sequence")
    def dir_import_widget(self,
        Directory_Path: pathlib.Path = pathlib.Path("~")) -> None:
        
        self.viewer.add_image(rw.read_stack(str(Directory_Path)), name = "Image")
    
    @magicgui(
        Method = {"choices": export_list},
        Save_Folder = {"mode": "d"},
        call_button = "Export Image(s)")
    def export_widget(self,
        Image: napari.layers.Image,
        Method: str = "Tiff",
        Multi_Page: bool = True,
        Save_Folder: pathlib.Path = pathlib.Path("~"),
        Save_Name: str = "Name") -> None:
        
        if Image.data.ndim == 3 and not Image.rgb:
            
            rw.write_stack(Image.data, str(Save_Folder), Save_Name, ext = Method.lower(), multi_page = Multi_Page)
        
        elif Image.data.ndim == 4:
            
            rw.write_stack(Image.data, str(Save_Folder), Save_Name, ext = Method.lower(), multi_page = Multi_Page)
        
        else:
            
            rw.write_im(Image.data, str(Save_Folder), Save_Name, Method.lower())


    # Transform Widgets

    @magicgui(
        Orientation = {"choices": reslice_list},
        call_button = "Reslice")
    def reslice_widget(self,
        Image: napari.layers.Image,
        Orientation: str = "Top",
        viewer: napari.viewer.Viewer = None) -> None:
        
        parameters_log.append(
            {"Reslice": {"Orientation": Orientation}})
        
        self.viewer.add_image(trans.reslice(Image.data, Orientation.lower()), name = "Reslice")
        
    @magicgui(
        Angle = {"widget_type": "FloatSlider", "max": 360},
        call_button = "Rotate")
    def rotate_widget(self,
        Image: napari.layers.Image,
        Clockwise: bool = False,
        Resize: bool = False,
        Angle: float = 0) -> None:
        
        parameters_log.append(
            {"Rotate": {"Clockwise": Clockwise,
                        "Resize": Resize,
                        "Angle": Angle}})
        
        if Clockwise:
            
            self.viewer.add_image(trans.rotate(Image.data, Angle, "CW", resize = Resize), name = "Rotate")
        
        else:
            
            self.viewer.add_image(trans.rotate(Image.data, Angle, resize = Resize), name = "Rotate")
        
    @magicgui(
        Axis = {"choices": mirror_list},
        call_button = "Mirror")
    def mirror_widget(self,
        Image: napari.layers.Image,
        Axis: int = 1) -> None:
        
        parameters_log.append(
            {"Mirror": {"Axis": Axis}})
        
        self.viewer.add_image(trans.mirror(Image.data, Axis), name = "Mirror")

    @magicgui(
        call_button = "Rescale Resolution")
    def rescale_widget(self,
            Image: napari.layers.Image,
            Scale: float = 0.5) -> None:
        
        parameters_log.append(
            {"Rescale": {"Scale": Scale}})
        
        self.viewer.add_image(trans.rescale(Image.data, Scale), name = "Rescale")


    # Histogram Widgets

    @magicgui(
        Type = {"choices": convert_type_list},
        call_button = "Convert Type")
    def convert_type_widget(self,
            Image: napari.layers.Image,
            Type: str = "Uint8",
            Auto_Normalize: bool = False,
            Bounds: bool = False,
            Min: float = 0,
            Max: float = 0) -> None:
        
        parameters_log.append(
            {"Convert Type": {"Type": Type,
                              "Auto Normalize": Auto_Normalize,
                              "Bounds": Bounds,
                              "Min": Min,
                              "Max": Max}})
        
        if Bounds:
            
            self.viewer.add_image(pixels.convert_im_type(Image.data, Type.lower(), norm = Auto_Normalize), name = Type)
        
        else:
            
            self.viewer.add_image(pixels.convert_im_type(Image.data, Type.lower(), norm = Auto_Normalize, float_bounds = (Min, Max)), name = Type)

    @magicgui(
        call_button = "Normalize")
    def normalize_widget(self,
            Image: napari.layers.Image,
            Input_Range: bool = False,
            Input_Min: float = 0,
            Input_Max: float = 0,
            Output_Range: bool = False,
            Output_Min: float = 0,
            Output_Max: float = 0) -> None:
        
        parameters_log.append(
            {"Normalize": {"Input Range": Input_Range,
                           "Output Range": Output_Range,
                           "Input Min": Input_Min,
                           "Input Max": Input_Max,
                           "Output Min": Output_Min,
                           "Output Max": Output_Max}})
        
        if Input_Range and Output_Range:
            
            self.viewer.add_image(pixels.normalize(Image.data, in_range = (Input_Min, Input_Max), out_range = (Output_Min, Output_Max)), name = "Normalize")
        
        elif Input_Range and not Output_Range:
            
            self.viewer.add_image(pixels.normalize(Image.data, in_range = (Input_Min, Input_Max)), name = "Normalize")
        
        elif Output_Range and not Input_Range:
            
            self.viewer.add_image(pixels.normalize(Image.data, out_range = (Output_Min, Output_Max)), name = "Normalize")

    @magicgui(
        call_button = "Saturate")
    def saturate_widget(self,
            Image: napari.layers.Image,
            Auto_Normalize: bool = False,
            Bounds_as_Percentages: bool = True,
            Min_Bound: float = 0,
            Max_Bound: float = 100) -> None:
        
        parameters_log.append(
            {"Saturate": {"Auto Normalize": Auto_Normalize,
                          "Bounds as Percentages": Bounds_as_Percentages,
                          "Min Bound": Min_Bound,
                          "Max Bound": Max_Bound}})
        
        self.viewer.add_image(pixels.saturate(Image.data, (Min_Bound, Max_Bound), auto_normalize = Auto_Normalize, bounds_as_percents = Bounds_as_Percentages), name = "Saturate")

    @magicgui(Method = {"choices": equalize_list},
              call_button = "Equalize Histogram")
    def equalize_widget(self,
            Image: napari.layers.Image,
            Method: str = "Global") -> None:
        
        parameters_log.append(
            {"Equalize": {"Method": Method}})
        
        self.viewer.add_image(pixels.equalize_histogram(Image.data, Method.lower()), name = "Equalize")

    @magicgui(
        call_button = "Invert Intensities")
    def invert_widget(self,
            Image: napari.layers.Image) -> None:
        
        parameters_log.append(
            {"Invert": {}})
        
        self.viewer.add_image(pixels.invert(Image.data), name = "Invert")
        
        
# Functions

def get_funcguis(magic_class) -> dict[str, widgets.FunctionGui]:
    
    return {name: obj for name, obj in magic_class.__dict__.items() if isinstance(obj, widgets.FunctionGui)}

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
        

def main() -> None:
    
    viewer: napari.viewer.Viewer = napari.Viewer()
    ui: ImageProcessor = ImageProcessor(viewer)
    tabs: QTabWidget = QTabWidget()
    
    mod_im_import_widget: widgets.Container = modify_funcgui(ui.im_import_widget, "Import Single File")
    mod_dir_import_widget: widgets.Container = modify_funcgui(ui.dir_import_widget, "Import File Sequence")
    mod_export_widget: widgets.Container = modify_funcgui(ui.export_widget, "Export Image(s)")
    io_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_im_import_widget, mod_dir_import_widget, mod_export_widget],
        labels = False)
    tabs.addTab(io_container.native, "I/O")
    
    mod_reslice_widget: widgets.Container = modify_funcgui(ui.reslice_widget, "Reslice")
    mod_rotate_widget: widgets.Container = modify_funcgui(ui.rotate_widget, "Rotate")
    mod_mirror_widget: widgets.Container = modify_funcgui(ui.mirror_widget, "Mirror")
    mod_rescale_widget: widgets.Container = modify_funcgui(ui.rescale_widget, "Rescale")
    trans_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_reslice_widget, mod_rotate_widget, mod_mirror_widget, mod_rescale_widget],
        labels = False)
    tabs.addTab(trans_container.native, "Transform")
    
    mod_convert_type: widgets.Container = modify_funcgui(ui.convert_type_widget, "Convert Type")
    mod_normalize: widgets.Container = modify_funcgui(ui.normalize_widget, "Normalize")
    mod_saturate: widgets.Container = modify_funcgui(ui.saturate_widget, "Saturate")
    mod_equalize: widgets.Container = modify_funcgui(ui.equalize_widget, "Equalize")
    mod_invert: widgets.Container = modify_funcgui(ui.invert_widget, "Invert")
    pixels_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_convert_type, mod_normalize, mod_saturate, mod_equalize, mod_invert],
        labels = False)
    tabs.addTab(pixels_container.native, "Histogram")
    
    tabs.setCurrentIndex(0)
    viewer.window.add_dock_widget(tabs, name = "Image Processing Tools")
    
if __name__ == "__main__":
    
    main()