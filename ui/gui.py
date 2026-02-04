"""
Module for PyDoug GUI
"""


# Imports

import magicclass.widgets as mcw
import sliceview as sv
import readwrite as rw
import cropclip as cc
import pathlib
import napari
import pixels
import trans
import util
import pywt

from qtpy.QtWidgets import QTabWidget
from magicclass import magicclass
from filtering import denoising
from magicgui import magicgui
from magicgui import widgets
from qtpy.QtCore import Qt


# Globals

parameters_log: list[dict[str, dict]] = []
export_list: list[str] = ["Tiff", "HDF5"]
trim_pad_list: list[str] = ["Trim", "Pad"]
shapes_list: list[str] = ["Ellipse", "Rectangle", "Polygon"]
out_of_mask_list: list[str] = ["Black", "White", "Gray"]
mask_method_list: list[str] = ["Out", "In"]
reslice_list: list[str] = ["Top", "Bottom", "Left", "Right", "Back"]
mirror_list: list[int] = ["X", "Y", "Z"]
convert_type_list: list[str] = ["Uint8", "Uint16", "Int16", "Float", "Float32", "Float64", "Bool"]
equalize_list: list[str] = ["Global", "Local", "Adaptive"]
bilateral_list: list[str] = ["Constant", "Edge", "Symmetric", "Reflect", "Wrap"]
gaussian_list: list[str] = ["Constant", "Mirror", "Nearest", "Reflect", "Wrap"]
wavelets_list: list[str] = pywt.wavelist()
wave_modes_list: list[str] = ["Soft", "Hard"]
wave_thresh_list: list[str] = ["BayesShrink", "VisuShrink"]
axes_dict_3d: dict[str, int] = {"X": 2, "Y": 1, "Z": 0}
axes_dict_2d: dict[str, int] = {"X": 1, "Y": 0}


# Classes

@magicclass
class ImageProcessor:
    
    def __init__(self, viewer: napari.viewer.Viewer) -> None:
        
        self.viewer: napari.viewer.Viewer = viewer
        self.viewer.layers.events.inserted.connect(self._on_layer_added)
        self.viewer.layers.events.changed.connect(self._on_layer_changed)
        self.funcguis: dict[str, widgets.FunctionGui] = get_funcguis(ImageProcessor)
        Epsilon: float = 0.001
        self.tv_bregman_widget.Epsilon.native.setDecimals(4)
        self.tv_bregman_widget.Epsilon.step = 0.0001
        self.tv_bregman_widget.Epsilon.value = Epsilon
        Epsilon: float =0.0002
        self.tv_chambolle_widget.Epsilon.native.setDecimals(4)
        self.tv_chambolle_widget.Epsilon.step = 0.0001
        self.tv_chambolle_widget.Epsilon.value = Epsilon
        
    def _on_layer_changed(self, event = None):
        
        for func_name in self.funcguis:
            
            funcgui: widgets.FunctionGui = getattr(self, func_name)
            
            if hasattr(funcgui, "Image"):
            
                funcgui.Image.reset_choices()
                funcgui.Image.value = sv.get_top_im_layer(self.viewer)
                
            if hasattr(funcgui, "Mask"):
            
                funcgui.Mask.reset_choices()
                funcgui.Mask.value = sv.get_top_im_layer(self.viewer)
        
    def _on_layer_added(self, event):
        
        layer = event.value
        
        if isinstance(layer, napari.layers.Image):
            
            for func_name in self.funcguis:
                
                funcgui: widgets.FunctionGui = getattr(self, func_name)
                
                if hasattr(funcgui, "Image"):
                
                    funcgui.Image.reset_choices()
                    funcgui.Image.value = layer
                    
                if hasattr(funcgui, "Mask"):
                
                    funcgui.Mask.reset_choices()
                    funcgui.Mask.value = sv.get_top_im_layer(self.viewer)
                    
        elif isinstance(layer, napari.layers.Shapes):
            
            for func_name in self.funcguis:
                
                funcgui: widgets.FunctionGui = getattr(self, func_name)
                
                if hasattr(funcgui, "Shapes"):
                
                    funcgui.Shapes.reset_choices()
                    funcgui.Shapes.value = layer
                
    
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
            
            
    # Manipulate Widgets
    
    @magicgui(
        Method = {"choices": trim_pad_list},
        Padded_Color = {"choices": out_of_mask_list},
        call_button = "Trim / Pad")
    def trim_pad_widget(self,
        Image: napari.layers.Image,
        Method: str = "Trim",
        Bounds_as_Slices: bool = False,
        X_Bounds: bool = True,
        X_Min: int = 0,
        X_Max: int = 0,
        Y_Bounds: bool = True,
        Y_Min: int = 0,
        Y_Max: int = 0,
        Z_Bounds: bool = True,
        Z_Min: int = 0,
        Z_Max: int = 0,
        Padded_Color: str = "Black",
        Specify_Color: bool = False,
        Color_Value: float = 0,
        Conserve_RAM: bool = False) -> None:
        
        if X_Bounds:
            
            x_bounds = [X_Min, X_Max]
            
        else:
            
            x_bounds = None
            
        if Y_Bounds:
            
            y_bounds = [Y_Min, Y_Max]
            
        else:
            
            y_bounds = None
            
        if Z_Bounds:
            
            z_bounds = [Z_Min, Z_Max]
            
        else:
            
            z_bounds = None
            
        bounds_dict = {"X": x_bounds, "Y": y_bounds, "Z": z_bounds}
        
        if Method == "Trim":
            
            parameters_log.append(
                {"Trim": {"X Bounds": x_bounds,
                          "Y Bounds": y_bounds,
                          "Z Bounds": z_bounds,
                          "Bounds as Slices": Bounds_as_Slices}})
            
            if Conserve_RAM:
                
                Image.data = cc.trim(Image.data, bounds_dict = bounds_dict, bounds_as_slices = Bounds_as_Slices, conserve_mem = True)
                Image.name = "Trimmed"
                self._on_layer_changed()
            
            else:
                
                self.viewer.add_image(cc.trim(Image.data, bounds_dict = bounds_dict, bounds_as_slices = Bounds_as_Slices), name = "Trimmed")
                
        elif Method == "Pad":
            
            if not Specify_Color:
                
                color_spec: float | int = util.convert_color_to_intensity(Image.data, Padded_Color)
            
            else:
                
                if Image.data.dtype in util.int_dtypes:
                    
                    color_spec: int = round(Color_Value)
                    
                else:
                    
                    color_spec = Color_Value
            
            parameters_log.append(
                {"Pad": {"X Bounds": x_bounds,
                         "Y Bounds": y_bounds,
                         "Z Bounds": z_bounds,
                         "Bounds as Slices": Bounds_as_Slices,
                         "Padded Color": color_spec}})
            
            if Conserve_RAM:
                
                Image.data = cc.pad(Image.data, bounds_dict = bounds_dict, bounds_as_slices = Bounds_as_Slices, padded_color = color_spec, conserve_mem = True)
                Image.name = "Padded"
                self._on_layer_changed()
            
            else:
                
                self.viewer.add_image(cc.pad(Image.data, bounds_dict = bounds_dict, bounds_as_slices = Bounds_as_Slices, padded_color = color_spec), name = "Padded")
    
    @magicgui(
        Shape_Type = {"choices": shapes_list},
        call_button = "Add Shape")
    def add_shape_widget(self,
        Shape_Type: str = "Ellipse",
        Polygon_Vertices: int = 3) -> None:
        
        sv.add_shape(self.viewer, Shape_Type.lower(), n_vertices = Polygon_Vertices)
    
    @magicgui(
        call_button = "Create Mask")
    def create_mask_widget(self,
        Image: napari.layers.Image,
        Shapes: napari.layers.Shapes) -> None:
        
        if util.is_3d_rgb(Image.data)["3D"]:
            
            self.viewer.add_image(cc.get_mask(Image.data, self.viewer, shapes_layer = Shapes), name = "Mask", opacity = 0.5)
            
        else:
            
            self.viewer.add_image(cc.get_mask(Image.data, self.viewer, shapes_layer = Shapes, convert_to_3d = False), name = "Mask", opacity = 0.5)
    
    @magicgui(
        Mask_Method = {"choices": mask_method_list},
        Masked_Color = {"choices": out_of_mask_list},
        call_button = "Mask")
    def mask_widget(self,
        Image: napari.layers.Image,
        Mask: napari.layers.Image,
        Mask_Method: str = "Out",
        Masked_Color: str = "Black",
        Specify_Color: bool = False,
        Color_Value: float = 0) -> None:
        
        if not Specify_Color:
            
            color_spec: float | int = util.convert_color_to_intensity(Image.data, Masked_Color)
        
        else:
            
            if Image.data.dtype in util.int_dtypes:
                
                color_spec: int = round(Color_Value)
                
            else:
                
                color_spec = Color_Value
                
        parameters_log.append(
            {"Mask": {"Method": Mask_Method.lower(),
                      "Masked Color": color_spec}})
                
        self.viewer.add_image(cc.mask(Image.data, Mask.data, method = Mask_Method.lower(), mask_color = color_spec), name = "Masked")
    
    @magicgui(
        Masked_Color = {"choices": out_of_mask_list},
        call_button = "Crop")
    def crop_widget(self,
        Image: napari.layers.Image,
        Mask: napari.layers.Image,
        Masked_Color: str = "Black",
        Specify_Color: bool = False,
        Color_Value: float = 0,
        Conserve_RAM: bool = False) -> None:
        
        if not Specify_Color:
            
            color_spec: float | int = util.convert_color_to_intensity(Image.data, Masked_Color)
        
        else:
            
            if Image.data.dtype in util.int_dtypes:
                
                color_spec: int = round(Color_Value)
                
            else:
                
                color_spec = Color_Value
        
        if Conserve_RAM:
            
            Image.data = cc.crop(Image.data, Mask.data, mask_color = color_spec, conserve_mem = True)
            Image.name = "Cropped"
            self._on_layer_changed()
        
        else:
            
            self.viewer.add_image(cc.crop(Image.data, Mask.data, mask_color = color_spec), name = "Cropped")


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
        
        self.viewer.add_image(trans.reslice(Image.data, Orientation.lower()), name = "Resliced")
        
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
            
            self.viewer.add_image(trans.rotate(Image.data, Angle, "CW", resize = Resize), name = "Rotated")
        
        else:
            
            self.viewer.add_image(trans.rotate(Image.data, Angle, resize = Resize), name = "Rotated")
        
    @magicgui(
        Direction = {"choices": mirror_list},
        call_button = "Mirror")
    def mirror_widget(self,
        Image: napari.layers.Image,
        Direction: str = "Y") -> None:
        
        Direction = util.convert_ax_str_to_int(Image.data, Image.rgb, Direction)
        parameters_log.append(
            {"Mirror": {"Direction": Direction}})
        
        self.viewer.add_image(trans.mirror(Image.data, Direction), name = "Mirrored")

    @magicgui(
        call_button = "Rescale Resolution")
    def rescale_widget(self,
            Image: napari.layers.Image,
            Scale: float = 0.5) -> None:
        
        parameters_log.append(
            {"Rescale": {"Scale": Scale}})
        
        self.viewer.add_image(trans.rescale(Image.data, Scale), name = "Rescaled")


    # Pixel Values Widgets

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
            
            self.viewer.add_image(pixels.normalize(Image.data, in_range = (Input_Min, Input_Max)), name = "Normalized")
        
        elif Output_Range and not Input_Range:
            
            self.viewer.add_image(pixels.normalize(Image.data, out_range = (Output_Min, Output_Max)), name = "Normalized")

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
        
        self.viewer.add_image(pixels.saturate(Image.data, (Min_Bound, Max_Bound), auto_normalize = Auto_Normalize, bounds_as_percents = Bounds_as_Percentages), name = "Saturated")

    @magicgui(Method = {"choices": equalize_list},
              call_button = "Equalize Histogram")
    def equalize_widget(self,
            Image: napari.layers.Image,
            Method: str = "Global") -> None:
        
        parameters_log.append(
            {"Equalize": {"Method": Method}})
        
        self.viewer.add_image(pixels.equalize_histogram(Image.data, Method.lower()), name = "Equalized")

    @magicgui(
        call_button = "Invert Intensities")
    def invert_widget(self,
            Image: napari.layers.Image) -> None:
        
        parameters_log.append(
            {"Invert": {}})
        
        self.viewer.add_image(pixels.invert(Image.data), name = "Inverted")
        
    
    # Denoising Widgets
    
    @magicgui(
        Edges_Method = {"choices": bilateral_list},
        call_button = "Bilateral Filter")
    def bilateral_widget(self,
            Image: napari.layers.Image,
            Window_Size: int = 0,
            Sigma_Color: float = 0.1,
            Sigma_Spatial: float = 1,
            Bins: int = 10000,
            Edges_Method: str = "Edge",
            Constant_Value: float = 0) -> None:
        
        if Window_Size == 0:
            
            Window_Size = None
        
        self.viewer.add_image(denoising.bilateral(Image.data,
                                                  win_size = Window_Size,
                                                  sigma_color = Sigma_Color,
                                                  sigma_spatial = Sigma_Spatial,
                                                  bins = Bins,
                                                  mode = Edges_Method.lower(),
                                                  cval = Constant_Value), name = "Bilateral Filter")
        
    @magicgui(
        Edges_Method = {"choices": gaussian_list},
        call_button = "Gaussian Blur")
    def gaussian_widget(self,
            Image: napari.layers.Image,
            Sigma: float = 1.0,
            Truncate: float = 4.0,
            Edges_Method: str = "Nearest",
            Constant_Value: float = 0) -> None:
        
        self.viewer.add_image(denoising.gaussian(Image.data,
                                                 sigma = Sigma,
                                                 truncate = Truncate,
                                                 mode = Edges_Method.lower(),
                                                 cval = Constant_Value), name = "Gaussian Blur")
        
    @magicgui(
        call_button = "Non-Local Means Filter")
    def nl_means_widget(self,
            Image: napari.layers.Image,
            Patch_Size: int = 7,
            Patch_Distance: int = 11,
            Cut_Off_Distance: float = 0.1,
            Sigma: float = 0) -> None:
        
        self.viewer.add_image(denoising.non_local_means(Image.data,
                                                        patch_size = Patch_Size,
                                                        patch_distance = Patch_Distance,
                                                        h = Cut_Off_Distance,
                                                        sigma = Sigma), name = "Non-Local Means Filter")
        
    @magicgui(
        call_button = "Remove Background")
    def remove_background_widget(self,
            Image: napari.layers.Image,
            Radius: int = 5) -> None:
        
        self.viewer.add_image(denoising.remove_background(Image.data,
                                                          radius = Radius), name = "Remove Background")
        
    @magicgui(
        call_button = "TV Bregman Filter")
    def tv_bregman_widget(self,
            Image: napari.layers.Image,
            Weight: float = 5.0,
            Epsilon: float = 0.001,
            Max_Iterations: int = 100,
            Isotropic: bool = True) -> None:
        
        self.viewer.add_image(denoising.tv_bregman(Image.data,
                                                   weight = Weight,
                                                   max_num_iter = Max_Iterations,
                                                   eps = Epsilon,
                                                   isotropic = Isotropic), name = "TV Bregman Filter")
    
    @magicgui(
        call_button = "TV Chambolle Filter")
    def tv_chambolle_widget(self,
            Image: napari.layers.Image,
            Weight: float = 0.1,
            Epsilon: float = 0.0002,
            Max_Iterations: int = 200) -> None:
        
        self.viewer.add_image(denoising.tv_chambolle(Image.data,
                                                     weight = Weight,
                                                     max_num_iter = Max_Iterations,
                                                     eps = Epsilon), name = "TV Chambolle Filter")
        
    @magicgui(
        Wavelet = {"choices": wavelets_list},
        Mode = {"choices": wave_modes_list},
        Threshold_Method = {"choices": wave_thresh_list},
        call_button = "Wavelet Filter")
    def wavelet_widget(self,
            Image: napari.layers.Image,
            Wavelet: str = "db1",
            Mode: str = "Soft",
            Sigma: float = None,
            Wavelet_Levels: int = None,
            Threshold_Method: str = "BayesShrink",
            Rescale_Sigma: bool = True) -> None:
        
        if Sigma == 0:
            
            Sigma = None
            
        if Wavelet_Levels == 0:
            
            Wavelet_Levels = None
        
        self.viewer.add_image(denoising.wavelet(Image.data,
                                                wavelet = Wavelet,
                                                mode = Mode.lower(),
                                                sigma = Sigma,
                                                wavelet_levels = Wavelet_Levels,
                                                method = Threshold_Method,
                                                rescale_sigma = Rescale_Sigma), name = "Wavelet Filter")
        
        
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


# Main        

def main() -> None:
    
    
    # Initialize
    
    viewer: napari.viewer.Viewer = napari.Viewer()
    ui: ImageProcessor = ImageProcessor(viewer)
    tabs: QTabWidget = QTabWidget()
    
    
    # I/O Widgets
    
    mod_im_import: widgets.Container = modify_funcgui(ui.im_import_widget, "Import Single File")
    mod_dir_import: widgets.Container = modify_funcgui(ui.dir_import_widget, "Import File Sequence")
    mod_export: widgets.Container = modify_funcgui(ui.export_widget, "Export Image(s)")
    io_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_im_import, mod_dir_import, mod_export],
        labels = False)
    tabs.addTab(io_container.native, "I/O")
    
    
    # Manipulate Widgets
    
    mod_trim_pad: widgets.Container = modify_funcgui(ui.trim_pad_widget, "Trim / Pad")
    mod_add_mask: widgets.Container = modify_funcgui(ui.add_shape_widget, "Add Shape")
    mod_create_mask: widgets.Container = modify_funcgui(ui.create_mask_widget, "Create Mask")
    mod_mask: widgets.Container = modify_funcgui(ui.mask_widget, "Mask")
    mod_crop: widgets.Container = modify_funcgui(ui.crop_widget, "Crop")
    manipulate_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_trim_pad, mod_add_mask, mod_create_mask, mod_mask, mod_crop],
        labels = False)
    tabs.addTab(manipulate_container.native, "Manipulate")
    
    
    # Transform Widgets
    
    mod_reslice: widgets.Container = modify_funcgui(ui.reslice_widget, "Reslice")
    mod_rotate: widgets.Container = modify_funcgui(ui.rotate_widget, "Rotate")
    mod_mirror: widgets.Container = modify_funcgui(ui.mirror_widget, "Mirror")
    mod_rescale: widgets.Container = modify_funcgui(ui.rescale_widget, "Rescale")
    trans_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_reslice, mod_rotate, mod_mirror, mod_rescale],
        labels = False)
    tabs.addTab(trans_container.native, "Transform")
    
    
    # Pixel Values Widgets
    
    mod_convert_type: widgets.Container = modify_funcgui(ui.convert_type_widget, "Convert Type")
    mod_normalize: widgets.Container = modify_funcgui(ui.normalize_widget, "Normalize")
    mod_saturate: widgets.Container = modify_funcgui(ui.saturate_widget, "Saturate")
    mod_equalize: widgets.Container = modify_funcgui(ui.equalize_widget, "Equalize")
    mod_invert: widgets.Container = modify_funcgui(ui.invert_widget, "Invert")
    pixels_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_convert_type, mod_normalize, mod_saturate, mod_equalize, mod_invert],
        labels = False)
    tabs.addTab(pixels_container.native, "Pixel Values")
    
    
    # Denoising Widgets
    
    mod_bilateral: widgets.Container = modify_funcgui(ui.bilateral_widget, "Bilateral Filter")
    mod_gaussian: widgets.Container = modify_funcgui(ui.gaussian_widget, "Gaussian Blur")
    mod_nl_means: widgets.Container = modify_funcgui(ui.nl_means_widget, "Non-Local Means Filter")
    mod_remove_background: widgets.Container = modify_funcgui(ui.remove_background_widget, "Remove Background")
    mod_tv_bregman: widgets.Container = modify_funcgui(ui.tv_bregman_widget, "TV Bregman Filter")
    mod_tv_chambolle: widgets.Container = modify_funcgui(ui.tv_chambolle_widget, "TV Chambolle Filter")
    mod_wavelet: widgets.Container = modify_funcgui(ui.wavelet_widget, "Wavelet Filter")
    denoising_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_bilateral, mod_gaussian, mod_nl_means, mod_remove_background, mod_tv_bregman, mod_tv_chambolle, mod_wavelet],
        labels = False)
    tabs.addTab(denoising_container.native, "Denoising")
    
    
    # Launch
    
    tabs.setCurrentIndex(0)
    viewer.window.add_dock_widget(tabs, name = "Image Processing Tools")
    
if __name__ == "__main__":
    
    main()