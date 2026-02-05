"""
Module for PyDoug GUI
"""


# Imports

import magicclass.widgets as mcw
import sliceview as sv
import readwrite as rw
import cropclip as cc
import numpy as np
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
from filtering import morph
from qtpy.QtCore import Qt
from segment import thresh
from segment import detect


# Globals

parameters_log: list[dict[str, dict]] = []

export_list: list[str] = ["Tiff", "HDF5"]

trim_pad_list: list[str] = ["Trim", "Pad"]
shapes_list: list[str] = ["Ellipse", "Rectangle", "Polygon"]
out_of_mask_list: list[str] = ["Black", "White", "Gray"]
mask_method_list: list[str] = ["Out", "In"]

reslice_list: list[str] = ["Top", "Bottom", "Left", "Right", "Back"]
axis_list: list[int] = ["X", "Y", "Z"]

convert_type_list: list[str] = ["Uint8", "Uint16", "Int16", "Float", "Float32", "Float64", "Bool"]
equalize_list: list[str] = ["Global", "Local", "Adaptive"]

bilateral_list: list[str] = ["Constant", "Edge", "Symmetric", "Reflect", "Wrap"]
gaussian_list: list[str] = ["Constant", "Mirror", "Nearest", "Reflect", "Wrap"]
wavelets_list: list[str] = pywt.wavelist()
wave_modes_list: list[str] = ["Soft", "Hard"]
wave_thresh_list: list[str] = ["BayesShrink", "VisuShrink"]

hist_thresh_list: list[str] = ["Isodata", "Li", "Mean", "Minimum", "Otsu", "Triangle", "Yen"]
local_thresh_list: list[str] = ["Adaptive", "Niblack", "Savoula"]
connectivity_list: list[int] = [1, 2, 3]
label_list: list[str] = ["Connectivity", "Watershed"]
morph_snakes_list: list[str] = ["ACWE", "GAC"]

axes_dict_3d: dict[str, int] = {"X": 2, "Y": 1, "Z": 0}
axes_dict_2d: dict[str, int] = {"X": 1, "Y": 0}

remove_objects_list: list[str] = ["Particles", "Holes"]
tophat_list: list[str] = ["Black", "White"]


# Classes

@magicclass
class ImageProcessor:
    
    def __init__(self, viewer: napari.viewer.Viewer) -> None:
        
        self.viewer: napari.viewer.Viewer = viewer
        
        self.viewer.layers.events.inserted.connect(self._on_layer_added)
        self.viewer.layers.events.changed.connect(self._on_layer_changed)
        self.viewer.layers.events.removed.connect(self._on_layer_removed)
        
        self.funcguis: dict[str, widgets.FunctionGui] = get_funcguis(ImageProcessor)
        self.operation_count: int = 0
        self.mask_count: int = 0
        
        Epsilon: float = 0.001
        self.tv_bregman_widget.Epsilon.native.setDecimals(4)
        self.tv_bregman_widget.Epsilon.step = 0.0001
        self.tv_bregman_widget.Epsilon.value = Epsilon
        Epsilon: float = 0.0002
        self.tv_chambolle_widget.Epsilon.native.setDecimals(4)
        self.tv_chambolle_widget.Epsilon.step = 0.0001
        self.tv_chambolle_widget.Epsilon.value = Epsilon
        
        self.manual_threshold_widget.Image.changed.connect(self._update_intensity_range)
        self.manual_threshold_widget.Range.changed.connect(self._live_threshold)
        self.manual_threshold_widget.Image.changed.connect(self._live_threshold)
        self.manual_threshold_widget.Preview.changed.connect(self._on_live_toggled)
        
        
    # Connector Methods
        
    def _on_layer_changed(self, event = None) -> None:
        
        for func_name in self.funcguis:
            
            funcgui: widgets.FunctionGui = getattr(self, func_name)
            
            if hasattr(funcgui, "Image"):
            
                funcgui.Image.reset_choices()
                funcgui.Image.value = sv.get_top_im_layer(self.viewer)
                
            if hasattr(funcgui, "Mask"):
            
                funcgui.Mask.reset_choices()
                funcgui.Mask.value = sv.get_top_im_layer(self.viewer)
                
        self.operation_count += 1
        
    def _on_layer_added(self, event) -> None:
        
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
                    
        self.operation_count += 1
        
    def _on_layer_removed(self, event) -> None:
        
        layer = event.value
        operations = [x["Name"] for x in parameters_log]
        
        if layer.name in operations:
            
            parameters_log.pop(operations.index(layer.name))
            
        if isinstance(layer, napari.layers.Image):
            
            for func_name in self.funcguis:
                
                funcgui: widgets.FunctionGui = getattr(self, func_name)
                
                if hasattr(funcgui, "Image"):
                
                    funcgui.Image.reset_choices()
                    
                if hasattr(funcgui, "Mask"):
                
                    funcgui.Mask.reset_choices()
                    
    def _update_intensity_range(self, event = None) -> None:
        
        if self.manual_threshold_widget.Image.value == None:
            
            return
        
        if np.issubdtype(self.manual_threshold_widget.Image.value.data.dtype, np.integer):
            
            if self.manual_threshold_widget.Image.value.data.dtype == np.int64:
                
                return
            
            info = np.iinfo(self.manual_threshold_widget.Image.value.data.dtype)
            
        else:
            
            info = np.finfo(self.manual_threshold_widget.Image.value.data.dtype)
            
        self.manual_threshold_widget.Range.min = info.min
        self.manual_threshold_widget.Range.max = info.max
        self.manual_threshold_widget.Range.value = (info.min, info.max)
        
    def _live_threshold(self, event = None) -> None:
        
        if not self.manual_threshold_widget.Preview.value:
            
            return
        
        im_layer = self.manual_threshold_widget.Image.value
        
        if im_layer == None:
            
            return
        
        min_value, max_value = self.manual_threshold_widget.Range.value
        threshold_mask: np.ndarray = thresh.gui_threshold(im_layer.data, (min_value, max_value))
        
        if hasattr(self, "_live_mask_layer") and self._live_mask_layer in self.viewer.layers:
            
            self._live_mask_layer.data = threshold_mask
            
        else:
            
            self._live_mask_layer = self.viewer.add_labels(threshold_mask, name = "Live Threshold")
            
    def _on_live_toggled(self, event = None) -> None:
        
        if not self.manual_threshold_widget.Preview.value:
            
            if hasattr(self, "_live_mask_layer") and self._live_mask_layer in self.viewer.layers:
                
                self.viewer.layers.remove(self._live_mask_layer)
            
                self._live_mask_layer = None
            
        else:
            
            self._live_threshold()
                
    
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
    def im_export_widget(self,
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
            
    @magicgui(
        Save_Folder = {"mode": "d"},
        call_button = "Export Parameters")
    def export_parameters_widget(self,
        Save_Folder: pathlib.Path = pathlib.Path("~"),
        File_Name: str = "Parameters") -> None:
        
        rw.write_parameters(parameters_log, str(File_Name), str(Save_Folder))
            
            
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
            
            param_layer_name: str = get_param_layer_name("Trimmed", self.operation_count)
            parameters_log.append(
                {"Name": param_layer_name,
                 "X Bounds": X_Bounds,
                 "X Min": X_Min,
                 "X Max": X_Max,
                 "Y Bounds": X_Bounds,
                 "Y Min": Y_Min,
                 "Y Max": Y_Max,
                 "Z Bounds": X_Bounds,
                 "Z Min": Z_Min,
                 "Z Max": Z_Max,
                 "Bounds as Slices": Bounds_as_Slices})
            
            if Conserve_RAM:
                
                Image.data = cc.trim(Image.data, bounds_dict = bounds_dict, bounds_as_slices = Bounds_as_Slices, conserve_mem = True)
                Image.name = param_layer_name
                self._on_layer_changed()
            
            else:
                
                self.viewer.add_image(cc.trim(Image.data, bounds_dict = bounds_dict, bounds_as_slices = Bounds_as_Slices), name = param_layer_name)
                
        elif Method == "Pad":
            
            if not Specify_Color:
                
                color_spec: float | int = util.convert_color_to_intensity(Image.data, Padded_Color)
            
            else:
                
                if Image.data.dtype in util.int_dtypes:
                    
                    color_spec: int = round(Color_Value)
                    
                else:
                    
                    color_spec = Color_Value
            
            param_layer_name: str = get_param_layer_name("Padded", self.operation_count)
            parameters_log.append(
                {"Name": param_layer_name,
                 "X Bounds": X_Bounds,
                 "X Min": X_Min,
                 "X Max": X_Max,
                 "Y Bounds": X_Bounds,
                 "Y Min": Y_Min,
                 "Y Max": Y_Max,
                 "Z Bounds": X_Bounds,
                 "Z Min": Z_Min,
                 "Z Max": Z_Max,
                 "Bounds as Slices": Bounds_as_Slices,
                 "Padded Color": color_spec})
            
            if Conserve_RAM:
                
                Image.data = cc.pad(Image.data, bounds_dict = bounds_dict, bounds_as_slices = Bounds_as_Slices, padded_color = color_spec, conserve_mem = True)
                Image.name = param_layer_name
                self._on_layer_changed()
            
            else:
                
                self.viewer.add_image(cc.pad(Image.data, bounds_dict = bounds_dict, bounds_as_slices = Bounds_as_Slices, padded_color = color_spec), name = param_layer_name)
    
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
        
        self.mask_count += 1
        param_layer_name: str = get_param_layer_name("Mask", self.mask_count)
        
        if util.is_3d_rgb(Image.data)["3D"]:
            
            self.viewer.add_image(cc.get_mask(Image.data, self.viewer, shapes_layer = Shapes), name = param_layer_name, opacity = 0.5)
            
        else:
            
            self.viewer.add_image(cc.get_mask(Image.data, self.viewer, shapes_layer = Shapes, convert_to_3d = False), name = param_layer_name, opacity = 0.5)
    
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
                
        param_layer_name = get_param_layer_name("Masked", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Method": Mask_Method.lower(),
             "Masked Color": color_spec})
        self.viewer.add_image(cc.mask(Image.data, Mask.data, method = Mask_Method.lower(), mask_color = color_spec), name = param_layer_name)
    
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
                
        param_layer_name = get_param_layer_name("Cropped", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Masked Color": color_spec})
        
        if Conserve_RAM:
            
            Image.data = cc.crop(Image.data, Mask.data, mask_color = color_spec, conserve_mem = True)
            Image.name = param_layer_name
            self._on_layer_changed()
        
        else:
            
            self.viewer.add_image(cc.crop(Image.data, Mask.data, mask_color = color_spec), name = param_layer_name)


    # Transform Widgets

    @magicgui(
        Orientation = {"choices": reslice_list},
        call_button = "Reslice")
    def reslice_widget(self,
        Image: napari.layers.Image,
        Orientation: str = "Top",
        viewer: napari.viewer.Viewer = None) -> None:
        
        param_layer_name = get_param_layer_name("Resliced", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Orientation": Orientation})
        self.viewer.add_image(trans.reslice(Image.data, Orientation.lower()), name = param_layer_name)
        
    @magicgui(
        Angle = {"widget_type": "FloatSlider", "max": 360},
        call_button = "Rotate")
    def rotate_widget(self,
        Image: napari.layers.Image,
        Clockwise: bool = False,
        Resize: bool = False,
        Angle: float = 0) -> None:
        
        param_layer_name = get_param_layer_name("Rotated", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Clockwise": Clockwise,
             "Resize": Resize,
             "Angle": Angle})
        
        if Clockwise:
            
            self.viewer.add_image(trans.rotate(Image.data, Angle, "CW", resize = Resize), name = param_layer_name)
        
        else:
            
            self.viewer.add_image(trans.rotate(Image.data, Angle, resize = Resize), name = param_layer_name)
        
    @magicgui(
        Direction = {"choices": axis_list},
        call_button = "Mirror")
    def mirror_widget(self,
        Image: napari.layers.Image,
        Direction: str = "Y") -> None:
        
        Direction = util.convert_ax_str_to_int(Image.data, Image.rgb, Direction)
        param_layer_name = get_param_layer_name("Mirrored", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Direction": Direction})
        self.viewer.add_image(trans.mirror(Image.data, Direction), name = param_layer_name)

    @magicgui(
        call_button = "Rescale")
    def rescale_widget(self,
        Image: napari.layers.Image,
        Scale: float = 0.5) -> None:
        
        param_layer_name = get_param_layer_name("Rescaled", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Scale": Scale})
        self.viewer.add_image(trans.rescale(Image.data, Scale), name = param_layer_name)


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
        
        param_layer_name = get_param_layer_name("Converted", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Type": Type,
             "Auto Normalize": Auto_Normalize,
             "Bounds": Bounds,
             "Min": Min,
             "Max": Max})
        
        if Bounds:
            
            self.viewer.add_image(pixels.convert_im_type(Image.data, Type.lower(), norm = Auto_Normalize), name = param_layer_name)
        
        else:
            
            self.viewer.add_image(pixels.convert_im_type(Image.data, Type.lower(), norm = Auto_Normalize, float_bounds = (Min, Max)), name = param_layer_name)

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
        
        param_layer_name = get_param_layer_name("Normalized", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Input Range": Input_Range,
             "Output Range": Output_Range,
             "Input Min": Input_Min,
             "Input Max": Input_Max,
             "Output Min": Output_Min,
             "Output Max": Output_Max})
        
        if Input_Range and Output_Range:
            
            self.viewer.add_image(pixels.normalize(Image.data, in_range = (Input_Min, Input_Max), out_range = (Output_Min, Output_Max)), name = param_layer_name)
        
        elif Input_Range and not Output_Range:
            
            self.viewer.add_image(pixels.normalize(Image.data, in_range = (Input_Min, Input_Max)), name = param_layer_name)
        
        elif Output_Range and not Input_Range:
            
            self.viewer.add_image(pixels.normalize(Image.data, out_range = (Output_Min, Output_Max)), name = param_layer_name)

    @magicgui(
        call_button = "Saturate")
    def saturate_widget(self,
        Image: napari.layers.Image,
        Auto_Normalize: bool = False,
        Bounds_as_Percentages: bool = True,
        Min_Bound: float = 0,
        Max_Bound: float = 100) -> None:
        
        param_layer_name = get_param_layer_name("Saturated", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Auto Normalize": Auto_Normalize,
             "Bounds as Percentages": Bounds_as_Percentages,
             "Min Bound": Min_Bound,
             "Max Bound": Max_Bound})
        self.viewer.add_image(pixels.saturate(Image.data, (Min_Bound, Max_Bound), auto_normalize = Auto_Normalize, bounds_as_percents = Bounds_as_Percentages), name = param_layer_name)

    @magicgui(Method = {"choices": equalize_list},
        call_button = "Equalize Histogram")
    def equalize_widget(self,
        Image: napari.layers.Image,
        Method: str = "Global") -> None:
        
        param_layer_name = get_param_layer_name("Equalized", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method})
        self.viewer.add_image(pixels.equalize_histogram(Image.data, Method.lower()), name = param_layer_name)

    @magicgui(
        call_button = "Invert")
    def invert_widget(self,
        Image: napari.layers.Image) -> None:
        
        param_layer_name = get_param_layer_name("Inverted", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name})
        self.viewer.add_image(pixels.invert(Image.data), name = param_layer_name)
        
    
    # Denoising Widgets
    
    @magicgui(
        Edges_Method = {"choices": bilateral_list},
        call_button = "Filter")
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
            
        param_layer_name = get_param_layer_name("Bilateral", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Window Size": Window_Size,
             "Sigma Color": Sigma_Color,
             "Sigma Spatial": Sigma_Spatial,
             "Bins": Bins,
             "Mode": Edges_Method.lower(),
             "CVal": Constant_Value})
        self.viewer.add_image(denoising.bilateral(Image.data,
                                                  win_size = Window_Size,
                                                  sigma_color = Sigma_Color,
                                                  sigma_spatial = Sigma_Spatial,
                                                  bins = Bins,
                                                  mode = Edges_Method.lower(),
                                                  cval = Constant_Value), name = param_layer_name)
        
    @magicgui(
        Edges_Method = {"choices": gaussian_list},
        call_button = "Filter")
    def gaussian_widget(self,
        Image: napari.layers.Image,
        Sigma: float = 1.0,
        Truncate: float = 4.0,
        Edges_Method: str = "Nearest",
        Constant_Value: float = 0) -> None:
        
        param_layer_name = get_param_layer_name("Gaussian", self.operation_count)
        parameters_log.append(
            {"name": param_layer_name,
             "Sigma": Sigma,
             "Truncate": Truncate,
             "Mode": Edges_Method.lower(),
             "CVal": Constant_Value})
        self.viewer.add_image(denoising.gaussian(Image.data,
                                                 sigma = Sigma,
                                                 truncate = Truncate,
                                                 mode = Edges_Method.lower(),
                                                 cval = Constant_Value), name = param_layer_name)
        
    @magicgui(
        call_button = "Filter")
    def nl_means_widget(self,
        Image: napari.layers.Image,
        Patch_Size: int = 7,
        Patch_Distance: int = 11,
        Cut_Off_Distance: float = 0.1,
        Sigma: float = 0) -> None:
        
        param_layer_name = get_param_layer_name("Non-Local Means", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Patch Size": Patch_Size,
             "Patch Distance": Patch_Distance,
             "Cut Off Distance": Cut_Off_Distance,
             "Sigma": Sigma})
        self.viewer.add_image(denoising.non_local_means(Image.data,
                                                        patch_size = Patch_Size,
                                                        patch_distance = Patch_Distance,
                                                        h = Cut_Off_Distance,
                                                        sigma = Sigma), name = param_layer_name)
        
    @magicgui(
        call_button = "Filter")
    def remove_background_widget(self,
        Image: napari.layers.Image,
        Radius: int = 5) -> None:
        
        param_layer_name = get_param_layer_name("Removed Background", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Radius": Radius})
        self.viewer.add_image(denoising.remove_background(Image.data,
                                                          radius = Radius), name = param_layer_name)
        
    @magicgui(
        call_button = "Filter")
    def tv_bregman_widget(self,
        Image: napari.layers.Image,
        Weight: float = 5.0,
        Epsilon: float = 0.001,
        Max_Iterations: int = 100,
        Isotropic: bool = True) -> None:
        
        param_layer_name = get_param_layer_name("TV Bregman", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Weight": Weight,
             "Epsilon": Epsilon,
             "Max Iterations": Max_Iterations,
             "Isotropic": Isotropic})
        self.viewer.add_image(denoising.tv_bregman(Image.data,
                                                   weight = Weight,
                                                   max_num_iter = Max_Iterations,
                                                   eps = Epsilon,
                                                   isotropic = Isotropic), name = param_layer_name)
    
    @magicgui(
        call_button = "Filter")
    def tv_chambolle_widget(self,
        Image: napari.layers.Image,
        Weight: float = 0.1,
        Epsilon: float = 0.0002,
        Max_Iterations: int = 200) -> None:
        
        param_layer_name = get_param_layer_name("TV Chambolle", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Weight": Weight,
             "Epsion": Epsilon,
             "Max Iterations": Max_Iterations})
        self.viewer.add_image(denoising.tv_chambolle(Image.data,
                                                     weight = Weight,
                                                     max_num_iter = Max_Iterations,
                                                     eps = Epsilon), name = param_layer_name)
        
    @magicgui(
        Wavelet = {"choices": wavelets_list},
        Mode = {"choices": wave_modes_list},
        Threshold_Method = {"choices": wave_thresh_list},
        call_button = "Filter")
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
            
        param_layer_name = get_param_layer_name("Wavelet", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Wavelet": Wavelet,
             "Mode": Mode.lower(),
             "Sigma": Sigma,
             "Wavelet Levels": Wavelet_Levels,
             "Threshold Method": Threshold_Method,
             "Rescale Sigma": Rescale_Sigma})
        self.viewer.add_image(denoising.wavelet(Image.data,
                                                wavelet = Wavelet,
                                                mode = Mode.lower(),
                                                sigma = Sigma,
                                                wavelet_levels = Wavelet_Levels,
                                                method = Threshold_Method,
                                                rescale_sigma = Rescale_Sigma), name = param_layer_name)
        
    
    # Segmentation Widgets
    
    @magicgui(
        Range = {"widget_type": "RangeSlider", "min": 0, "max": 255},
        call_button = "Segment")
    def manual_threshold_widget(self,
        Image: napari.layers.Image,
        Preview: bool = False,
        Range = (0, 255)) -> None:
        
        param_layer_name = get_param_layer_name("Manual Threshold", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Min": min(Range),
             "Max": max(Range)})
        self.viewer.add_image(thresh.gui_threshold(Image.data, Range), name = param_layer_name)
    
    @magicgui(
        Method = {"choices": hist_thresh_list},
        call_button = "Segment")
    def hist_threshold_widget(self,
        Image: napari.layers.Image,
        Method: str = "Otsu",
        Otsu_Classes: int = 2,
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None) -> None:
        
        param_layer_name = get_param_layer_name("Histogram Threshold", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method.lower(),
             "Otsu Classes": Otsu_Classes,
             "Apply Mask": Apply_Mask})
        
        if Apply_Mask:
            
            self.viewer.add_image(thresh.hist(Image.data, method = Method.lower(), otsu_classes = Otsu_Classes, mask_array = Mask.data), name = param_layer_name)
        
        else:
            
            self.viewer.add_image(thresh.hist(Image.data, method = Method.lower(), otsu_classes = Otsu_Classes), name = param_layer_name)
    
    @magicgui(
        Method = {"choices": local_thresh_list},
        call_button = "Segment")
    def local_threshold_widget(self,
        Image: napari.layers.Image,
        Method: str = "Adaptive",
        Window_Size: int = 3,
        Niblack_or_Savoula_Sigma_Weight: float = 0.2,
        Savoula_Sigma_Range: float = 0,
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None) -> None:
        
        if Savoula_Sigma_Range == 0:
            
            Savoula_Sigma_Range = None
        
        param_layer_name = get_param_layer_name("Local Threshold", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method.lower(),
             "Window Size": Window_Size,
             "Sigma Weight": Niblack_or_Savoula_Sigma_Weight,
             "Sigma Range": Savoula_Sigma_Range,
             "Apply Mask": Apply_Mask})
        
        if Apply_Mask:
            
            self.viewer.add_image(thresh.local(Image.data, mask_array = Mask.data, method = Method.lower(), block_size = Window_Size, window_size = Window_Size, k = Niblack_or_Savoula_Sigma_Weight, r = Savoula_Sigma_Range), name = param_layer_name)
            
        else:
            
            self.viewer.add_image(thresh.local(Image.data, method = Method.lower(), block_size = Window_Size, window_size = Window_Size, k = Niblack_or_Savoula_Sigma_Weight, r = Savoula_Sigma_Range), name = param_layer_name)
    
    @magicgui(
        Method = {"choices": label_list},
        Connectivity = {"choices": connectivity_list},
        Axis = {"choices": axis_list},
        call_button = "Label Segmentation")
    def label_widget(self,
        Image: napari.layers.Image,
        Method: str = "Connectivity",
        Background: int = 0,
        Connectivity: int = 3,
        Along_Axis: bool = False,
        Axis: str = "Z",
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None) -> None:
        
        Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)
        
        if Method == "Connectivity":
        
            if Connectivity > Image.data.ndim:
                
                Connectivity = 2
                
            elif Connectivity > 2 and Along_Axis:
                
                Connectivity = 2
                
            param_layer_name = get_param_layer_name("Label", self.operation_count)
            parameters_log.append(
                {"Name": param_layer_name,
                 "Background": Background,
                 "Connectivity": Connectivity,
                 "Along Axis": Along_Axis,
                 "Axis": Axis,
                 "Apply Mask": Apply_Mask})
            
            if Apply_Mask:
                
                self.viewer.add_image(thresh.label(Image.data, mask_array = Mask.data, connectivity = Connectivity, background = Background, positional = Along_Axis, axis = Axis), name = param_layer_name)
            
            else:
                
                self.viewer.add_image(thresh.label(Image.data, connectivity = Connectivity, background = Background, positional = Along_Axis, axis = Axis), name = param_layer_name)
                
        elif Method == "Watershed":
            
            param_layer_name = get_param_layer_name("Watershed", self.operation_count)
            parameters_log.append(
                {"Name": param_layer_name,
                 "Background": Background,
                 "Along Axis": Along_Axis,
                 "Axis": Axis,
                 "Apply Mask": Apply_Mask})
            
            if Apply_Mask:
                
                self.viewer.add_image(detect.watershed(Image.data, background = Background, mask_array = Mask.data, along_axis = Along_Axis, axis = Axis), name = param_layer_name)
            
            else:
                
                self.viewer.add_image(detect.watershed(Image.data, background = Background, along_axis = Along_Axis, axis = Axis), name = param_layer_name)
            
    @magicgui(
        call_button = "Segment")
    def rand_walk_widget(self,
        Image: napari.layers.Image,
        Beta: float = 130,
        Lower_Percentile: float = 5,
        Upper_Percentile: float = 95) -> None:
        
        param_layer_name = get_param_layer_name("Random Walk", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Beta": Beta,
             "Lower Percentile": Lower_Percentile,
             "Upper Percentile": Lower_Percentile})
        self.viewer.add_image(detect.random_walk(Image.data, (Lower_Percentile, Upper_Percentile), Beta), name = param_layer_name)
    
    @magicgui(
        Method = {"choices": morph_snakes_list},
        call_button = "Segment")
    def morph_snakes_widget(self,
        Image: napari.layers.Image,
        Method: str = "ACWE",
        Iterations: int = 10,
        Square_Size: int = 5,
        GAC_Alpha: float = 100,
        GAC_Sigma: float = 5,
        GAC_Smoothing: int = 1) -> None:
        
        param_layer_name = get_param_layer_name("Morph Snakes", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method,
             "Iterations": Iterations,
             "Square Size": Square_Size,
             "Alpha": GAC_Alpha,
             "Sigma": GAC_Sigma,
             "Smoothing": GAC_Smoothing})
        self.viewer.add_image(detect.morph_snakes(Image.data, Method,
                                                  square_size = Square_Size,
                                                  num_iter = Iterations,
                                                  smoothing = GAC_Smoothing,
                                                  alpha = GAC_Alpha,
                                                  sigma = GAC_Sigma), name = param_layer_name)
    
    
    # Filter Widgets
    
    @magicgui(
        Method = {"choices": remove_objects_list},
        call_button = "Remove Objects")
    def remove_objects_widget(self,
        Image: napari.layers.Image,
        Method: str = "Particles",
        Connectivity: int = 3,
        Max_Size: float = 25,
        Background: int = 0,
        Pixel_Scale: int = 1) -> None:
        
        if Connectivity > Image.data.ndim:
            
            Connectivity = 2
            
        param_layer_name = get_param_layer_name("Remove Objects", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method.lower(),
             "Connectivity": Connectivity,
             "Max Size": Max_Size,
             "Background": Background,
             "Pixel Size": Pixel_Scale})
        self.viewer.add_image(morph.remove_objects(Image.data, Max_Size, Method.lower(), background = Background, pixel_size = Pixel_Scale, connectivity = Connectivity, ), name = param_layer_name)
    
    @magicgui(
        call_button = "Dilate")
    def dilate_widget(self,
        Image: napari.layers.Image,
        Iterations: int = 1,
        Along_Z_Axis: bool = False) -> None:
        
        param_layer_name = get_param_layer_name("Dilation", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Iterations": Iterations,
             "Along Axis": Along_Z_Axis})
        self.viewer.add_image(morph.dilation(Image.data, Iterations, along_axis = Along_Z_Axis), name = param_layer_name)
    
    @magicgui(
        call_button = "Erode")
    def erode_widget(self,
        Image: napari.layers.Image,
        Iterations: int = 1,
        Along_Z_Axis: bool = False) -> None:
        
        param_layer_name = get_param_layer_name("Erosion", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Iterations": Iterations,
             "Along Axis": Along_Z_Axis})
        self.viewer.add_image(morph.erosion(Image.data, Iterations, along_axis = Along_Z_Axis), name = param_layer_name)
    
    @magicgui(
        call_button = "Close")
    def close_widget(self,
        Image: napari.layers.Image,
        Dilations: int = 1,
        Erosions: int = 1,
        Along_Z_Axis: bool = False) -> None:
        
        param_layer_name = get_param_layer_name("Closing", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Dilations": Dilations,
             "Erosions": Erosions,
             "Along Axis": Along_Z_Axis})
        self.viewer.add_image(morph.closing(Image.data, Dilations, Erosions, along_axis = Along_Z_Axis), name = param_layer_name)
    
    @magicgui(
        call_button = "Open")
    def open_widget(self,
        Image: napari.layers.Image,
        Erosions: int = 1,
        Dilations: int = 1,
        Along_Z_Axis: bool = False) -> None:
        
        param_layer_name = get_param_layer_name("Opening", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Erosions": Erosions,
             "Dilations": Dilations,
             "Along Axis": Along_Z_Axis})
        self.viewer.add_image(morph.opening(Image.data, Erosions, Dilations, along_axis = Along_Z_Axis), name = param_layer_name)
    
    @magicgui(
        Method = {"choices": tophat_list},
        call_button = "Top Hat")
    def tophat_widget(self,
        Image: napari.layers.Image,
        Method: str = "Black",
        Dilations: int = 1,
        Erosions: int = 1,
        Along_Z_Axis: bool = False) -> None:
        
        param_layer_name = get_param_layer_name("Top Hat", self.operation_count)
        parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method,
             "Dilations": Dilations,
             "Erosions": Erosions,
             "Along Axis": Along_Z_Axis})
        self.viewer.add_image(morph.tophat(Image.data, Method, Dilations, Erosions, along_axis = Along_Z_Axis), name = param_layer_name)
    
    @magicgui(
        call_button = "Detect Edges")
    def edge_detect_widget(self,
        Image: napari.layers.Image) -> None:
        
        pass
    
    @magicgui(
        call_button = "Detect Corners")
    def corner_detect_widget(self,
        Image: napari.layers.Image) -> None:
        
        pass
    
    @magicgui(
        call_button = "FFT")
    def fft_widget(self,
        Image: napari.layers.Image) -> None:
        
        pass
    
    @magicgui(
        call_button = "IFFT")
    def ifft_widget(self,
        Image: napari.layers.Image) -> None:
        
        pass
        
        
# Functions

def get_param_layer_name(operation_name: str, operation_count: int) -> str:
    
    return f"{operation_name} [{operation_count}]"

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
    mod_im_export: widgets.Container = modify_funcgui(ui.im_export_widget, "Export Image(s)")
    mod_param_export: widgets.Container = modify_funcgui(ui.export_parameters_widget, "Export Parameters")
    io_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_im_import, mod_dir_import, mod_im_export, mod_param_export],
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
    mod_equalize: widgets.Container = modify_funcgui(ui.equalize_widget, "Equalize Histogram")
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
    
    
    # Segmentation Widgets
    
    mod_manual_threshold: widgets.Container = modify_funcgui(ui.manual_threshold_widget, "Manual Threshold")
    mod_label: widgets.Container = modify_funcgui(ui.label_widget, "Label")
    mod_hist_threshold: widgets.Container = modify_funcgui(ui.hist_threshold_widget, "Histogram Threshold")
    mod_local_threshold: widgets.Container = modify_funcgui(ui.local_threshold_widget, "Local Threshold")
    mod_rand_walk: widgets.Container = modify_funcgui(ui.rand_walk_widget, "Random Walk")
    mod_morph_snakes: widgets.Container = modify_funcgui(ui.morph_snakes_widget, "Morphological Snakes")
    segmentation_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_manual_threshold, mod_label, mod_hist_threshold, mod_local_threshold, mod_rand_walk, mod_morph_snakes],
        labels = False)
    tabs.addTab(segmentation_container.native, "Segmentation")
    
    
    # Filters
    
    mod_remove_objects: widgets.Container = modify_funcgui(ui.remove_objects_widget, "Remove Small Objects")
    mod_dilate: widgets.Container = modify_funcgui(ui.dilate_widget, "Dilation")
    mod_erode: widgets.Container = modify_funcgui(ui.erode_widget, "Erosion")
    mod_close: widgets.Container = modify_funcgui(ui.close_widget, "Closing")
    mod_open: widgets.Container = modify_funcgui(ui.open_widget, "Opening")
    mod_tophat: widgets.Container = modify_funcgui(ui.tophat_widget, "Top Hat")
    mod_edge_detect: widgets.Container = modify_funcgui(ui.edge_detect_widget, "Edge Detection")
    mod_corner_detect: widgets.Container = modify_funcgui(ui.corner_detect_widget, "Corner Detection")
    mod_fft: widgets.Container = modify_funcgui(ui.fft_widget, "FFT")
    mod_ifft: widgets.Container = modify_funcgui(ui.ifft_widget, "Inverse FFT")
    filter_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_remove_objects, mod_dilate, mod_erode, mod_close, mod_open, mod_tophat, mod_edge_detect, mod_corner_detect, mod_fft, mod_ifft],
        labels = False)
    tabs.addTab(filter_container.native, "Filters")
    
    
    # Launch
    
    tabs.setCurrentIndex(0)
    viewer.window.add_dock_widget(tabs, name = "Image Processing Tools")
    
if __name__ == "__main__":
    
    main()