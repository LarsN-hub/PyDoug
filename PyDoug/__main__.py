"""
Entry point for PyDoug GUI
"""


# Imports

import magicclass.widgets as mcw
import numpy as np
import pathlib
import napari
import pywt
import os

from matplotlib import pyplot as plt, colormaps
from magicgui import magicgui, widgets
from qtpy.QtWidgets import QTabWidget
from magicclass import magicclass
from qtpy.QtCore import Qt

from PyDoug.ui import sliceview as sv, readwrite as rw, batch
from PyDoug.proc import cropclip as cc, denoising, detect, fourier, morph, pixels, thresh, trans, util
from PyDoug.analyze import quant, plots


# Globals

version_str: str = "v0.6.1-alpha"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"


# Classes

@magicclass
class ImageProcessor:
    
    def __init__(self, viewer: napari.viewer.Viewer) -> None:
        
        self.viewer: napari.viewer.Viewer = viewer
        self.parameters_log: list[dict[str, dict]] = []
        
        self.viewer.layers.events.inserted.connect(self._on_layer_added)
        self.viewer.layers.events.changed.connect(self._on_layer_changed)
        self.viewer.layers.events.removed.connect(self._on_layer_removed)
        
        self.funcguis: dict[str, widgets.FunctionGui] = get_funcguis(ImageProcessor)
        self.operation_count: int = 0
        self.mask_count: int = 0
        
        self.rescale_widget.Scale.native.setDecimals(3)
        self.rescale_widget.Scale.step = 0.001
        self.rescale_widget.Scale.value = 0.5
        self.tv_bregman_widget.Epsilon.native.setDecimals(4)
        self.tv_bregman_widget.Epsilon.step = 0.0001
        self.tv_bregman_widget.Epsilon.value = 0.001
        self.tv_chambolle_widget.Epsilon.native.setDecimals(4)
        self.tv_chambolle_widget.Epsilon.step = 0.0001
        self.tv_chambolle_widget.Epsilon.value = 0.0002
        self.remove_objects_widget.Pixel_Scale.native.setDecimals(3)
        self.remove_objects_widget.Pixel_Scale.step = 0.001
        self.remove_objects_widget.Pixel_Scale.value = 1
        self.corner_detect_widget.Harris_Epsilon.native.setDecimals(6)
        self.corner_detect_widget.Harris_Epsilon.step = 0.000001
        self.corner_detect_widget.Harris_Epsilon.value = 0.000001
        self.histogram_widget.Y_Max.native.setDecimals(3)
        self.histogram_widget.Y_Max.step = 0.001
        self.histogram_widget.Y_Max.value = 0
        self.misc_calc_widget.Pixel_Scale.native.setDecimals(3)
        self.misc_calc_widget.Pixel_Scale.step = 0.001
        self.misc_calc_widget.Pixel_Scale.value = 1
        self.axis_distribution_widget.Pixel_Scale.native.setDecimals(3)
        self.axis_distribution_widget.Pixel_Scale.step = 0.001
        self.axis_distribution_widget.Pixel_Scale.value = 1
        self.psd_widget.Pixel_Scale.native.setDecimals(3)
        self.psd_widget.Pixel_Scale.step = 0.001
        self.psd_widget.Pixel_Scale.value = 1
        self.heat_map_widget.Pixel_Scale.native.setDecimals(3)
        self.heat_map_widget.Pixel_Scale.step = 0.001
        self.heat_map_widget.Pixel_Scale.value = 1
        self.heat_map_widget.Min_Value.native.setDecimals(3)
        self.heat_map_widget.Min_Value.step = 0.001
        self.heat_map_widget.Min_Value.value = 0
        self.heat_map_widget.Max_Value.native.setDecimals(3)
        self.heat_map_widget.Max_Value.step = 0.001
        self.heat_map_widget.Max_Value.value = 0
        self.image_2_labels_widget.Min_Value.native.setDecimals(3)
        self.image_2_labels_widget.Min_Value.step = 0.001
        self.image_2_labels_widget.Min_Value.value = 0
        self.image_2_labels_widget.Max_Value.native.setDecimals(3)
        self.image_2_labels_widget.Max_Value.step = 0.001
        self.image_2_labels_widget.Max_Value.value = 0
        self.image_2_labels_widget.Pixel_Scale.native.setDecimals(3)
        self.image_2_labels_widget.Pixel_Scale.step = 0.001
        self.image_2_labels_widget.Pixel_Scale.value = 1
        
        self.manual_threshold_widget.Image.changed.connect(self._update_intensity_range)
        self.manual_threshold_widget.Range.changed.connect(self._live_threshold)
        self.manual_threshold_widget.Image.changed.connect(self._live_threshold)
        self.manual_threshold_widget.Preview.changed.connect(self._on_live_toggled)
        
        
    #####################
    # Connector Methods #
    #####################
        
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
                    
                if hasattr(funcgui, "Image_1"):
                
                    funcgui.Image_1.reset_choices()
                    funcgui.Image_1.value = layer
                    
                if hasattr(funcgui, "Image_2"):
                
                    funcgui.Image_2.reset_choices()
                    funcgui.Image_2.value = layer
                    
                if hasattr(funcgui, "Mask"):
                
                    funcgui.Mask.reset_choices()
                    funcgui.Mask.value = layer
                    
                if hasattr(funcgui, "Mask_1"):
                
                    funcgui.Mask_1.reset_choices()
                    funcgui.Mask_1.value = layer
                    
                if hasattr(funcgui, "Mask_2"):
                
                    funcgui.Mask_2.reset_choices()
                    funcgui.Mask_2.value = layer
                    
        elif isinstance(layer, napari.layers.Shapes):
            
            for func_name in self.funcguis:
                
                funcgui: widgets.FunctionGui = getattr(self, func_name)
                
                if hasattr(funcgui, "Shapes"):
                
                    funcgui.Shapes.reset_choices()
                    funcgui.Shapes.value = layer
                    
        elif isinstance(layer, napari.layers.Labels):
            
            for func_name in self.funcguis:
                
                funcgui: widgets.FunctionGui = getattr(self, func_name)
                    
                if hasattr(funcgui, "Labels"):
                    
                    funcgui.Labels.reset_choices()
                    funcgui.Labels.value = layer
                    
                if hasattr(funcgui, "Paint"):
                
                    funcgui.Paint.reset_choices()
                    funcgui.Paint.value = layer
                    
        self.operation_count += 1
        
    def _on_layer_removed(self, event) -> None:
        
        layer = event.value
        operations = [x["Name"] for x in self.parameters_log]
        
        if layer.name in operations:
            
            self.parameters_log.pop(operations.index(layer.name))
            
        if isinstance(layer, napari.layers.Image):
            
            image_layers = [lyr for lyr in self.viewer.layers if isinstance(lyr, napari.layers.Image)]
            last_image = image_layers[-1] if image_layers else None
            
            for func_name in self.funcguis:
                
                funcgui: widgets.FunctionGui = getattr(self, func_name)
                
                if hasattr(funcgui, "Image"):
                
                    funcgui.Image.reset_choices()
                    
                    if last_image is not None:
                        
                        funcgui.Image.value = last_image
                    
                if hasattr(funcgui, "Mask"):
                
                    funcgui.Mask.reset_choices()
                    
                    if last_image is not None:
                        
                        funcgui.Mask.value = last_image
                    
                if hasattr(funcgui, "Mask_1"):
                
                    funcgui.Mask_1.reset_choices()
                    
                    if last_image is not None:
                        
                        funcgui.Mask_1.value = last_image
                        
                if hasattr(funcgui, "Mask_2"):
                
                    funcgui.Mask_2.reset_choices()
                    
                    if last_image is not None:
                        
                        funcgui.Mask_2.value = last_image
                        
        elif isinstance(layer, napari.layers.Shapes):
            
            shapes_layers = [lyr for lyr in self.viewer.layers if isinstance(lyr, napari.layers.Shapes)]
            last_shapes = shapes_layers[-1] if shapes_layers else None
            
            for func_name in self.funcguis:
                
                funcgui: widgets.FunctionGui = getattr(self, func_name)
                
                if hasattr(funcgui, "Shapes"):
                
                    funcgui.Shapes.reset_choices()
                    
                    if last_shapes is not None:
                        
                        funcgui.Shapes.value = last_shapes
        
        elif isinstance(layer, napari.layers.Labels):
            
            labels_layers = [lyr for lyr in self.viewer.layers if isinstance(lyr, napari.layers.Labels)]
            last_labels = labels_layers[-1] if labels_layers else None
            
            for func_name in self.funcguis:
                
                funcgui: widgets.FunctionGui = getattr(self, func_name)
                
                if hasattr(funcgui, "Labels"):
                    
                    funcgui.Labels.reset_choices()
                    
                    if last_labels is not None:
                        
                        funcgui.Labels.value = last_labels
                        
                if hasattr(funcgui, "Paint"):
                    
                    funcgui.Paint.reset_choices()
                    
                    if last_labels is not None:
                        
                        funcgui.Paint.value = last_labels
                    
    def _update_intensity_range(self, event = None) -> None:
        
        if self.manual_threshold_widget.Image.value == None:
            
            return
        
        if np.issubdtype(self.manual_threshold_widget.Image.value.data.dtype, np.integer):
            
            if self.manual_threshold_widget.Image.value.data.dtype == np.int64:
                
                return
            
            info = np.iinfo(self.manual_threshold_widget.Image.value.data.dtype)
            
        elif np.issubdtype(self.manual_threshold_widget.Image.value.data.dtype, np.floating):
            
            return
            
        else:
            
            return
            
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
            
            self._live_mask_layer = self.viewer.add_labels(threshold_mask, name = "Live Threshold", opacity = 0.4)
            
    def _on_live_toggled(self, event = None) -> None:
        
        if not self.manual_threshold_widget.Preview.value:
            
            if hasattr(self, "_live_mask_layer") and self._live_mask_layer in self.viewer.layers:
                
                self.viewer.layers.remove(self._live_mask_layer)
            
                self._live_mask_layer = None
            
        else:
            
            self._live_threshold()
                
    
    ###############
    # I/O Widgets #
    ###############
    
    @magicgui(
        call_button = "Import File")
    def im_import_widget(self,
        File_Path: pathlib.Path = pathlib.Path("~")) -> None:
        
        self.viewer.add_image(rw.read_stack(str(File_Path)), name = "Image")
    
    @magicgui(
        Directory_Path = {"mode": "d"},
        call_button = "Import File Sequence")
    def dir_import_widget(self,
        Directory_Path: pathlib.Path = pathlib.Path("~")) -> None:
        
        self.viewer.add_image(rw.read_stack(str(Directory_Path)), name = "Image")
    
    @magicgui(
        Method = {"choices": ["Tiff", "HDF5"]},
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
        Folder_Name: str = "Parameters",
        Compress_Masks: bool = False) -> None:
        
        save_dir: str = str(Save_Folder) + "/" + str(Folder_Name)
        os.makedirs(save_dir)
        rw.write_parameters(self.parameters_log, "Parameters", save_dir, viewer = self.viewer, compress_masks = Compress_Masks)
        
    @magicgui(
        Method = {"choices": ["Tiff", "HDF5"]},
        Save_Folder = {"mode": "d"},
        call_button = "Export Labels")
    def lab_export_widget(self,
        Labels: napari.layers.Labels,
        Method: str = "Tiff",
        Multi_Page: bool = True,
        Save_Folder: pathlib.Path = pathlib.Path("~"),
        Save_Name: str = "Name") -> None:
        
        if Labels.data.ndim == 3:
            
            rw.write_stack(Labels.data, str(Save_Folder), Save_Name, ext = Method.lower(), multi_page = Multi_Page)

        else:
            
            rw.write_im(Labels.data, str(Save_Folder), Save_Name, Method.lower())
        
    @magicgui(
        Save_Folder = {"mode": "d"},
        call_button = "Capture Screenshot")
    def screenshot_widget(self,
        Save_Folder: pathlib.Path = pathlib.Path("~"),
        Save_Name: str = "Name",
        Add_as_Parameter: bool = False) -> None:
        
        param_layer_name = get_param_layer_name("Screenshot", self.operation_count)
        
        if Add_as_Parameter:
            
            topmost_visible_layer: napari.layers.Layer = sv.get_topmost_visible_layer(self.viewer)
            
            if topmost_visible_layer:
                
                opacity: float = topmost_visible_layer.opacity
                blending: str = topmost_visible_layer.blending
                
            else:
                
                opacity: float = 0
                blending: str = "translucent"
            
            parameters_append: dict = {
                "Name": param_layer_name,
                "Center 0": self.viewer.camera.center[0],
                "Center 1": self.viewer.camera.center[1],
                "Center 2": self.viewer.camera.center[2],
                "Zoom": self.viewer.camera.zoom,
                "Angle 0": self.viewer.camera.angles[0],
                "Angle 1": self.viewer.camera.angles[1],
                "Angle 2": self.viewer.camera.angles[2],
                "Perspective": self.viewer.camera.perspective,
                "Orientation Depth": self.viewer.camera.orientation[0],
                "Orientation Vert": self.viewer.camera.orientation[1],
                "Orientation Horiz": self.viewer.camera.orientation[2],
                "Blending": blending,
                "Opacity": opacity,
                "Layer Type": util.get_layer_type(topmost_visible_layer),
                "Dimensions": self.viewer.dims.ndisplay}
            
            if parameters_append["Layer Type"] == "labels":
                
                parameters_append["ISO Gradient Mode"] = topmost_visible_layer.iso_gradient_mode
                parameters_append["Rendering"] = topmost_visible_layer.rendering
                parameters_append["Colormap Used"] = topmost_visible_layer.name
                
            elif parameters_append["Layer Type"] == "image":
                
                parameters_append["Contrast Min"] = topmost_visible_layer.contrast_limits[0]
                parameters_append["Contrast Max"] = topmost_visible_layer.contrast_limits[1]
                parameters_append["Gamma"] = topmost_visible_layer.gamma
                parameters_append["Projection Mode"] = topmost_visible_layer.projection_mode
                parameters_append["Rendering"] = topmost_visible_layer.rendering
                parameters_append["Interpolation 2D"] = topmost_visible_layer.interpolation2d
                parameters_append["Interpolation 3D"] = topmost_visible_layer.interpolation3d
                parameters_append["Colormap"] = topmost_visible_layer.colormap.name
                parameters_append["Depiction"] = topmost_visible_layer.depiction
                parameters_append["ISO Threshold"] = topmost_visible_layer.iso_threshold
                
            self.parameters_log.append(parameters_append)
        
        rw.write_im(sv.get_screenshot(self.viewer), str(Save_Folder), Save_Name)
    
    @magicgui(
        Image_Format = {"choices": ["Singles", "Stacks"]},
        Stack_Format = {"choices": ["Multi-Page", "Sequence"]},
        call_button = "Run Batch Script")
    def batch_widget(self,
        Image_Format: str = "Stacks",
        Stack_Format: str = "Multi-Page",
        Export_Images: bool = True,
        Export_Multi_Page: bool = True,
        Copy_Parameters: bool = False) -> None:
        
        batch.main(Image_Format, Stack_Format, Export_Images, Export_Multi_Page, Copy_Parameters)
            
            
    ######################
    # Manipulate Widgets #
    ######################
    
    @magicgui(
        Method = {"choices": ["Trim", "Pad"]},
        X_Min = {"max": 10000},
        X_Max = {"max": 10000},
        Y_Min = {"max": 10000},
        Y_Max = {"max": 10000},
        Z_Min = {"max": 10000},
        Z_Max = {"max": 10000},
        Padded_Color = {"choices": ["Black", "White", "Gray"]},
        Color_Value = {"max": 65535},
        call_button = "Trim / Pad")
    def trim_pad_widget(self,
        Image: napari.layers.Image,
        Method: str = "Trim",
        Bounds_as_Slices: bool = True,
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
            self.parameters_log.append(
                {"Name": param_layer_name,
                 "X Bounds": X_Bounds,
                 "X Min": X_Min,
                 "X Max": X_Max,
                 "Y Bounds": Y_Bounds,
                 "Y Min": Y_Min,
                 "Y Max": Y_Max,
                 "Z Bounds": Z_Bounds,
                 "Z Min": Z_Min,
                 "Z Max": Z_Max,
                 "Bounds as Slices": Bounds_as_Slices})
            
            if Conserve_RAM:
                
                Image.data = cc.trim(Image.data,
                                     bounds_dict = bounds_dict,
                                     bounds_as_slices = Bounds_as_Slices,
                                     conserve_mem = True)
                Image.name = param_layer_name
                self._on_layer_changed()
            
            else:
                
                self.viewer.add_image(cc.trim(Image.data,
                                              bounds_dict = bounds_dict,
                                              bounds_as_slices = Bounds_as_Slices), name = param_layer_name)
                
        elif Method == "Pad":
            
            if not Specify_Color:
                
                color_spec: float | int = util.convert_color_to_intensity(Image.data, Padded_Color)
            
            else:
                
                if Image.data.dtype in util.int_dtypes:
                    
                    color_spec: int = round(Color_Value)
                    
                else:
                    
                    color_spec = Color_Value
            
            param_layer_name: str = get_param_layer_name("Padded", self.operation_count)
            self.parameters_log.append(
                {"Name": param_layer_name,
                 "X Bounds": X_Bounds,
                 "X Min": X_Min,
                 "X Max": X_Max,
                 "Y Bounds": Y_Bounds,
                 "Y Min": Y_Min,
                 "Y Max": Y_Max,
                 "Z Bounds": Z_Bounds,
                 "Z Min": Z_Min,
                 "Z Max": Z_Max,
                 "Bounds as Slices": Bounds_as_Slices,
                 "Padded Color": color_spec})
            
            if Conserve_RAM:
                
                Image.data = cc.pad(Image.data,
                                    bounds_dict = bounds_dict,
                                    bounds_as_slices = Bounds_as_Slices,
                                    padded_color = color_spec,
                                    conserve_mem = True)
                Image.name = param_layer_name
                self._on_layer_changed()
            
            else:
                
                self.viewer.add_image(cc.pad(Image.data,
                                             bounds_dict = bounds_dict,
                                             bounds_as_slices = Bounds_as_Slices,
                                             padded_color = color_spec), name = param_layer_name)
    
    @magicgui(
        Masked_Color = {"choices": ["Black", "White", "Gray"]},
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
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Masked Color": color_spec,
             "Apply Mask": True,
             "Mask Used": Mask.name})
        
        if Conserve_RAM:
            
            Image.data = cc.crop(Image.data, Mask.data,
                                 mask_color = color_spec,
                                 conserve_mem = True)
            Image.name = param_layer_name
            self._on_layer_changed()
        
        else:
            
            self.viewer.add_image(cc.crop(Image.data, Mask.data,
                                          mask_color = color_spec), name = param_layer_name)
            
    @magicgui(
        Split_Index = {"max": 10000},
        Axis = {"choices": ["X", "Y", "Z"]},
        call_button = "Split")
    def split_widget(self,
        Image: napari.layers.Image,
        Split_Index: int = 0,
        Axis: str = "Z") -> None:
        
        Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)
        param_layer_name = get_param_layer_name("Split", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Split Index": Split_Index,
             "Axis": Axis})
        split_arrays: list[np.ndarray] = cc.split(Image.data, Split_Index, Axis)
        self.viewer.add_image(split_arrays[0], name = f"{param_layer_name} - 1")
        self.viewer.add_image(split_arrays[1], name = f"{param_layer_name} - 2")
        
    @magicgui(
        Axis = {"choices": ["X", "Y", "Z"]},
        call_button = "Join")
    def join_widget(self,
        Image_1: napari.layers.Image,
        Image_2: napari.layers.Image,
        Axis: str = "Z") -> None:
        
        Axis = util.convert_ax_str_to_int(Image_1.data, Image_1.rgb, Axis)
        param_layer_name = get_param_layer_name("Joined", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Axis": Axis})
        self.viewer.add_image(cc.join([Image_1.data, Image_2.data], Axis), name = param_layer_name)
        
    @magicgui(
        call_button = "Extend")
    def extend_widget(self,
        Image: napari.layers.Image,
        Slice_Count: int = 10,
        Add_as_Parameter: bool = False) -> None:
        
        param_layer_name = get_param_layer_name("Extended", self.operation_count)
        
        if Add_as_Parameter:
            
            self.parameters_log.append(
                {"Name": param_layer_name,
                 "Slice Count": Slice_Count})
        
        self.viewer.add_image(cc.project_mask(Image.data, num_slices = Slice_Count - 1), name = param_layer_name)
    
    
    #####################
    # Transform Widgets #
    #####################

    @magicgui(
        Orientation = {"choices": ["Top", "Bottom", "Left", "Right", "Back"]},
        call_button = "Reslice")
    def reslice_widget(self,
        Image: napari.layers.Image,
        Orientation: str = "Top",
        viewer: napari.viewer.Viewer = None) -> None:
        
        param_layer_name = get_param_layer_name("Resliced", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Orientation": Orientation.lower()})
        self.viewer.add_image(trans.reslice(Image.data, Orientation.lower()), name = param_layer_name)
        
    @magicgui(
        Angle = {"max": 360},
        call_button = "Rotate")
    def rotate_widget(self,
        Image: napari.layers.Image,
        Clockwise: bool = False,
        Resize: bool = False,
        Angle: float = 0) -> None:
        
        param_layer_name = get_param_layer_name("Rotated", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Clockwise": Clockwise,
             "Resize": Resize,
             "Angle": Angle})
        
        if Clockwise:
            
            self.viewer.add_image(trans.rotate(Image.data, Angle, "CW", resize = Resize), name = param_layer_name)
        
        else:
            
            self.viewer.add_image(trans.rotate(Image.data, Angle, resize = Resize), name = param_layer_name)
        
    @magicgui(
        Direction = {"choices": ["X", "Y", "Z"]},
        call_button = "Mirror")
    def mirror_widget(self,
        Image: napari.layers.Image,
        Direction: str = "Y") -> None:
        
        Direction = util.convert_ax_str_to_int(Image.data, Image.rgb, Direction)
        param_layer_name = get_param_layer_name("Mirrored", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Direction": Direction})
        self.viewer.add_image(trans.mirror(Image.data, Direction), name = param_layer_name)
        
    @magicgui(
        call_button = "Resize")
    def resize_widget(self,
        Image: napari.layers.Image,
        X_Dim: int = 0,
        Y_Dim: int = 0,
        Z_Dim: int = 0) -> None:
        
        param_layer_name: str = get_param_layer_name("Resized", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "X Dim": X_Dim,
             "Y Dim": Y_Dim,
             "Z Dim": Z_Dim})
        
        if X_Dim == 0:
            
            X_Dim: int = util.get_ax_str_dim(Image.data, "x")
            
        if Y_Dim == 0:
            
            Y_Dim: int = util.get_ax_str_dim(Image.data, "y")
            
        if Z_Dim == 0:
            
            Z_Dim: int | None = util.get_ax_str_dim(Image.data, "z")
            
        if Z_Dim:
            
            dims: tuple = (Z_Dim, Y_Dim, X_Dim)
            
        else:
            
            dims: tuple = (Y_Dim, X_Dim)
            
        self.viewer.add_image(trans.resize(Image.data, dims), name = param_layer_name)

    @magicgui(
        call_button = "Rescale")
    def rescale_widget(self,
        Image: napari.layers.Image,
        Scale: float = 0.5) -> None:
        
        param_layer_name: str = get_param_layer_name("Rescaled", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Scale": Scale})
        self.viewer.add_image(trans.rescale(Image.data, Scale), name = param_layer_name)
        
    
    ###################
    # Masking Widgets #
    ###################
    
    @magicgui(
        Mask_Method = {"choices": ["Out", "In"]},
        Masked_Color = {"choices": ["Black", "White", "Gray"]},
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
                
        param_layer_name: str = get_param_layer_name("Masked", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Method": Mask_Method.lower(),
             "Masked Color": color_spec,
             "Apply Mask": True,
             "Mask Used": Mask.name})
        self.viewer.add_image(cc.mask(Image.data, Mask.data,
                                      method = Mask_Method.lower(),
                                      mask_color = color_spec),
                              name = param_layer_name)
    
    @magicgui(
        Shape_Type = {"choices": ["Rectangle", "Ellipse", "Polygon", "Line"]},
        call_button = "Add Shape")
    def add_shape_widget(self,
        Shape_Type: str = "Rectangle",
        Polygon_Vertices: int = 3) -> None:
        
        sv.add_shape(self.viewer, Shape_Type.lower(), n_vertices = Polygon_Vertices)
    
    @magicgui(
        Slice_Start = {"max": 10000},
        Slice_End = {"max": 10000},
        call_button = "Create Mask")
    def create_shape_mask_widget(self,
        Image: napari.layers.Image,
        Shapes: napari.layers.Shapes,
        Specify_Slice_Range: bool = False,
        Slice_Start: int = 0,
        Slice_End: int = 0) -> None:
        
        self.mask_count += 1
        param_layer_name: str = get_param_layer_name("Mask", self.mask_count)
        
        if util.is_3d_rgb(Image.data)["3D"]:
            
            if Specify_Slice_Range:
            
                self.viewer.add_image(cc.get_mask(Image.data, self.viewer,
                                                  shapes_layer = Shapes,
                                                  slice_range = (Slice_Start, Slice_End)),
                                      name = param_layer_name, opacity = 0.5)
                
            else:
                
                self.viewer.add_image(cc.get_mask(Image.data, self.viewer,
                                                  shapes_layer = Shapes),
                                      name = param_layer_name, opacity = 0.5)
            
        else:
            
            self.viewer.add_image(cc.get_mask(Image.data, self.viewer,
                                              shapes_layer = Shapes,
                                              convert_to_3d = False),
                                  name = param_layer_name, opacity = 0.5)
    
    @magicgui(
        call_button = "Paint")
    def paint_widget(self,
        Image: napari.layers.Image) -> None:
        
        if util.is_3d_rgb(Image.data)["RGB"]:
            
            sv.create_label_layer(pixels.rgb_2_gray(Image.data), self.viewer)
        
        else:
        
            sv.create_label_layer(Image.data, self.viewer)
    
    @magicgui(
        call_button = "Create Mask")
    def create_paint_mask_widget(self,
        Paint: napari.layers.Labels) -> None:
        
        self.mask_count += 1
        param_layer_name: str = get_param_layer_name("Mask", self.mask_count)
        mask_array: np.ndarray = Paint.data
        mask_array[mask_array != 0] = 1
        mask_array = np.bool(mask_array)
        self.viewer.add_image(mask_array, name = param_layer_name, opacity = 0.5)
        
    @magicgui(Method = {"choices": ["Union", "Subtract", "Intersect"]},
        call_button = "Perform Operation")
    def mask_logic_widget(self,
        Mask_1: napari.layers.Image,
        Mask_2: napari.layers.Image,
        Method: str = "Union") -> None:
        
        self.mask_count += 1
        param_layer_name: str = get_param_layer_name("Mask", self.operation_count)
        self.viewer.add_image(cc.mask_logic(Mask_1.data, Mask_2.data, Method.lower()),
                              name = param_layer_name, opacity = 0.5)


    ########################
    # Pixel Values Widgets #
    ########################

    @magicgui(
        Type = {"choices": ["Uint8", "Uint16", "Int16", "Float", "Float32", "Float64", "Bool"]},
        Min = {"max": 65535, "min": -65535},
        Max = {"max": 65535, "min": -65535},
        call_button = "Convert Type")
    def convert_type_widget(self,
        Image: napari.layers.Image,
        Type: str = "Uint8",
        Auto_Normalize: bool = True,
        Bounds: bool = False,
        Min: float = 0,
        Max: float = 0) -> None:
        
        param_layer_name = get_param_layer_name("Converted", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Type": Type.lower(),
             "Auto Normalize": Auto_Normalize,
             "Bounds": Bounds,
             "Min": Min,
             "Max": Max})
        
        if Bounds:
            
            self.viewer.add_image(pixels.convert_im_type(Image.data, Type.lower(),
                                                         norm = Auto_Normalize),
                                  name = param_layer_name)
        
        else:
            
            self.viewer.add_image(pixels.convert_im_type(Image.data, Type.lower(),
                                                         norm = Auto_Normalize,
                                                         float_bounds = (Min, Max)),
                                  name = param_layer_name)

    @magicgui(
        Input_Min = {"max": 65535, "min": -65535},
        Input_Max = {"max": 65535, "min": -65535},
        Output_Min = {"max": 65535, "min": -65535},
        Output_Max = {"max": 65535, "min": -65535},
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
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Input Range": Input_Range,
             "Output Range": Output_Range,
             "Input Min": Input_Min,
             "Input Max": Input_Max,
             "Output Min": Output_Min,
             "Output Max": Output_Max})
        
        if Input_Range:
            
            in_range: tuple = (Input_Min, Input_Max)
            
        else:
            
            in_range: str = "image"
            
        if Output_Range:
            
            out_range: tuple = (Output_Min, Output_Max)
            
        else:
            
            out_range: str = "dtype"
        
        self.viewer.add_image(pixels.normalize(Image.data,
                                               in_range = in_range,
                                               out_range = out_range),
                              name = param_layer_name)

    @magicgui(
        Min_Bound = {"max": 65535, "min": -65535},
        Max_Bound = {"max": 65535, "min": -65535},
        call_button = "Saturate")
    def saturate_widget(self,
        Image: napari.layers.Image,
        Auto_Normalize: bool = True,
        Bounds_as_Percentages: bool = True,
        Min_Bound: float = 0,
        Max_Bound: float = 100,
        Parameterize_Percentages: bool = False,
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None) -> None:
        
        if Apply_Mask:
            
            mask_array: np.ndarray = Mask.data
            mask_name: str = Mask.name
            
        else:
            
            mask_array: None = None
            mask_name: None = None
        
        if Bounds_as_Percentages:
            
            bounds = quant.get_percent_intensities(Image.data, (Min_Bound, Max_Bound), mask_array = mask_array)
            
        else:
            
            bounds = (Min_Bound, Max_Bound)
        
        if Parameterize_Percentages and Bounds_as_Percentages:
            
            param_min: float = Min_Bound
            param_max: float = Max_Bound
            param_bounds_as_percentages: bool = True
            
        else:
            
            param_min: float = min(bounds)
            param_max: float = max(bounds)
            param_bounds_as_percentages: bool = False
            
        param_layer_name = get_param_layer_name("Saturated", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Auto Normalize": Auto_Normalize,
             "Bounds as Percentages": param_bounds_as_percentages,
             "Min Bound": param_min,
             "Max Bound": param_max,
             "Apply Mask": Apply_Mask,
             "Mask Used": mask_name})
        self.viewer.add_image(pixels.saturate(Image.data, bounds,
                                              auto_normalize = Auto_Normalize,
                                              bounds_as_percents = False),
                              name = param_layer_name)

    @magicgui(
        Method = {"choices": ["Global", "Local", "Adaptive"]},
        Axis = {"choices": ["X", "Y", "Z"]},
        call_button = "Equalize Histogram")
    def equalize_widget(self,
        Image: napari.layers.Image,
        Method: str = "Global",
        Local_Radius: int = 3,
        Along_Axis: bool = False,
        Axis: str = "Z",
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None) -> None:
        
        if not Apply_Mask:
            
            mask_name = None
            mask_array = None
            
        else:
            
            mask_name = Mask.name
            mask_array = Mask.data
        
        Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)
        param_layer_name = get_param_layer_name("Equalized", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method.lower(),
             "Local Radius": Local_Radius,
             "Along Axis": Along_Axis,
             "Axis": Axis,
             "Apply Mask": Apply_Mask,
             "Mask Used": mask_name})
        self.viewer.add_image(pixels.equalize_histogram(Image.data, Method.lower(),
                                                        mask_array = mask_array, 
                                                        radius = Local_Radius,
                                                        along_axis = Along_Axis,
                                                        axis = Axis),
                              name = param_layer_name)
        
    @magicgui(
        Input_Intensity = {"max": 65535, "min": -65535},
        Output_Intensity = {"max": 65535, "min": -65535},
        call_button = "Re-Assign")
    def reassign_widget(self,
        Image: napari.layers.Image,
        Input_Intensity: float = 0,
        Output_Intensity: float = 0) -> None:
        
        param_layer_name = get_param_layer_name("Re-assigned", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Input Intensity": Input_Intensity,
             "Output Intensity": Output_Intensity})
        new_array: np.ndarray = np.copy(Image.data)
        new_array[new_array == Input_Intensity] = Output_Intensity
        self.viewer.add_image(new_array, name = param_layer_name)
        
    @magicgui(
        call_button = "Grayscale")
    def grayscale_widget(self,
        Image: napari.layers.Image) -> None:
        
        param_layer_name = get_param_layer_name("Grayscale", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name})
        self.viewer.add_image(pixels.rgb_2_gray(Image.data), name = param_layer_name)
        
    @magicgui(
        call_button = "Invert")
    def invert_widget(self,
        Image: napari.layers.Image) -> None:
            
        param_layer_name = get_param_layer_name("Inverted", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name})
        self.viewer.add_image(pixels.invert(Image.data), name = param_layer_name)
        
    
    #####################
    # Denoising Widgets #
    #####################
    
    @magicgui(
        Axis = {"choices": ["X", "Y", "Z"]},
        Edges_Method = {"choices": ["Constant", "Edge", "Symmetric", "Reflect", "Wrap"]},
        Constant_Value = {"max": 65535},
        call_button = "Filter")
    def bilateral_widget(self,
        Image: napari.layers.Image,
        Axis: str = "Z",
        Window_Size: int = 0,
        Sigma_Color: float = 0.1,
        Sigma_Spatial: float = 1,
        Bins: int = 10000,
        Edges_Method: str = "Edge",
        Constant_Value: float = 0) -> None:
        
        Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)            
        param_layer_name = get_param_layer_name("Bilateral", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Axis": Axis,
             "Window Size": Window_Size,
             "Sigma Color": Sigma_Color,
             "Sigma Spatial": Sigma_Spatial,
             "Bins": Bins,
             "Mode": Edges_Method.lower(),
             "CVal": Constant_Value})
        
        if Window_Size == 0:
            
            Window_Size = None
        
        self.viewer.add_image(denoising.bilateral(Image.data,
                                                  axis = Axis,
                                                  win_size = Window_Size,
                                                  sigma_color = Sigma_Color,
                                                  sigma_spatial = Sigma_Spatial,
                                                  bins = Bins,
                                                  mode = Edges_Method.lower(),
                                                  cval = Constant_Value), name = param_layer_name)
        
    @magicgui(
        Edges_Method = {"choices": ["Constant", "Mirror", "Nearest", "Reflect", "Wrap"]},
        Constant_Value = {"max": 65535},
        Axis = {"choices": ["X", "Y", "Z"]},
        call_button = "Filter")
    def gaussian_widget(self,
        Image: napari.layers.Image,
        Sigma: float = 1.0,
        Truncate: float = 4.0,
        Edges_Method: str = "Nearest",
        Constant_Value: float = 0,
        Along_Axis: bool = False,
        Axis: str = "Z") -> None:
        
        Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)
        param_layer_name = get_param_layer_name("Gaussian", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Sigma": Sigma,
             "Truncate": Truncate,
             "Mode": Edges_Method.lower(),
             "Along Axis": Along_Axis,
             "Axis": Axis,
             "CVal": Constant_Value})
        self.viewer.add_image(denoising.gaussian(Image.data,
                                                 sigma = Sigma,
                                                 truncate = Truncate,
                                                 mode = Edges_Method.lower(),
                                                 cval = Constant_Value,
                                                 axial = Along_Axis,
                                                 axis = Axis), name = param_layer_name)
        
    @magicgui(
        Axis = {"choices": ["X", "Y", "Z"]},
        call_button = "Filter")
    def nl_means_widget(self,
        Image: napari.layers.Image,
        Patch_Size: int = 7,
        Patch_Distance: int = 11,
        Cut_Off_Distance: float = 0.1,
        Sigma: float = 0,
        Along_Axis: bool = False,
        Axis: str = "Z") -> None:
        
        Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)
        param_layer_name = get_param_layer_name("Non-Local Means", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Patch Size": Patch_Size,
             "Patch Distance": Patch_Distance,
             "Cut Off Distance": Cut_Off_Distance,
             "Sigma": Sigma,
             "Along Axis": Along_Axis,
             "Axis": Axis})
        self.viewer.add_image(denoising.non_local_means(Image.data,
                                                        patch_size = Patch_Size,
                                                        patch_distance = Patch_Distance,
                                                        h = Cut_Off_Distance,
                                                        sigma = Sigma,
                                                        axial = Along_Axis,
                                                        axis = Axis), name = param_layer_name)
        
    @magicgui(
        call_button = "Filter")
    def remove_background_widget(self,
        Image: napari.layers.Image,
        Radius: int = 5) -> None:
        
        param_layer_name = get_param_layer_name("Removed Background", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Radius": Radius})
        self.viewer.add_image(denoising.remove_background(Image.data,
                                                          radius = Radius), name = param_layer_name)
        
    @magicgui(
        Method = {"choices": ["FFT", "Wavelet"]},
        Wavelet = {"choices": pywt.wavelist()},
        Square_Axis = {"choices": ["X", "Y", "Z"]},
        call_button = "Filter")
    def ring_removal_widget(self,
        Image: napari.layers.Image,
        Method: str = "FFT",
        FFT_Freq_Cutoff: int = 20,
        FFT_Filter_Order: int = 8,
        FFT_Rows: int = 1,
        Wavelet: str = "db9",
        Wavelet_Level: int = 5,
        Wavelet_Damping_Size: int = 1,
        Sorting: bool = False,
        Square_Axis: str = "Z") -> None:
        
        Square_Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Square_Axis)
        param_layer_name = get_param_layer_name("Ring Removal", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method,
             "FFT Freq Cutoff": FFT_Freq_Cutoff,
             "FFT Filter Order": FFT_Filter_Order,
             "FFT Rows": FFT_Rows,
             "Wavelet": Wavelet,
             "Wavelet Level": Wavelet_Level,
             "Wavelet Damping Size": Wavelet_Damping_Size,
             "Sorting": Sorting,
             "Square Axis": Square_Axis})
        
        if Method == "FFT":
            
            self.viewer.add_image(fourier.fft_ring_removal(Image.data,
                                                           cutoff_freq = FFT_Freq_Cutoff,
                                                           filter_order = FFT_Filter_Order,
                                                           rows = FFT_Rows,
                                                           sorting = Sorting,
                                                           square_axis = Square_Axis), name = param_layer_name)
            
        elif Method == "Wavelet":
            
            self.viewer.add_image(fourier.wavelet_ring_removal(Image.data,
                                                               level = Wavelet_Level,
                                                               size = Wavelet_Damping_Size,
                                                               wavelet = Wavelet,
                                                               sorting = Sorting,
                                                               square_axis = Square_Axis), name = param_layer_name)
        
    @magicgui(
        Axis = {"choices": ["X", "Y", "Z"]},
        call_button = "Filter")
    def tv_bregman_widget(self,
        Image: napari.layers.Image,
        Weight: float = 5.0,
        Epsilon: float = 0.001,
        Max_Iterations: int = 100,
        Isotropic: bool = True,
        Along_Axis: bool = False,
        Axis: str = "Z") -> None:
        
        Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)
        param_layer_name = get_param_layer_name("TV Bregman", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Weight": Weight,
             "Epsilon": Epsilon,
             "Max Iterations": Max_Iterations,
             "Isotropic": Isotropic,
             "Along Axis": Along_Axis,
             "Axis": Axis})
        self.viewer.add_image(denoising.tv_bregman(Image.data,
                                                   weight = Weight,
                                                   max_num_iter = Max_Iterations,
                                                   eps = Epsilon,
                                                   isotropic = Isotropic,
                                                   axial = Along_Axis,
                                                   axis = Axis), name = param_layer_name)
    
    @magicgui(
        Axis = {"choices": ["X", "Y", "Z"]},
        call_button = "Filter")
    def tv_chambolle_widget(self,
        Image: napari.layers.Image,
        Weight: float = 0.1,
        Epsilon: float = 0.0002,
        Max_Iterations: int = 200,
        Along_Axis: bool = False,
        Axis: str = "Z") -> None:
        
        Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)
        param_layer_name = get_param_layer_name("TV Chambolle", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Weight": Weight,
             "Epsilon": Epsilon,
             "Max Iterations": Max_Iterations,
             "Along Axis": Along_Axis,
             "Axis": Axis})
        self.viewer.add_image(denoising.tv_chambolle(Image.data,
                                                     weight = Weight,
                                                     max_num_iter = Max_Iterations,
                                                     eps = Epsilon,
                                                     axial = Along_Axis,
                                                     axis = Axis), name = param_layer_name)
        
    @magicgui(
        Wavelet = {"choices": pywt.wavelist()},
        Mode = {"choices": ["Soft", "Hard"]},
        Threshold_Method = {"choices": ["BayesShrink", "VisuShrink"]},
        Axis = {"choices": ["X", "Y", "Z"]},
        call_button = "Filter")
    def wavelet_widget(self,
        Image: napari.layers.Image,
        Wavelet: str = "db1",
        Mode: str = "Soft",
        Sigma: float = None,
        Wavelet_Levels: int = None,
        Threshold_Method: str = "BayesShrink",
        Rescale_Sigma: bool = True,
        Along_Axis: bool = False,
        Axis: str = "Z") -> None:
            
        Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)
        param_layer_name = get_param_layer_name("Wavelet", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Wavelet": Wavelet,
             "Mode": Mode.lower(),
             "Sigma": Sigma,
             "Wavelet Levels": Wavelet_Levels,
             "Threshold Method": Threshold_Method,
             "Rescale Sigma": Rescale_Sigma,
             "Along Axis": Along_Axis,
             "Axis": Axis})
        
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
                                                rescale_sigma = Rescale_Sigma,
                                                axial = Along_Axis,
                                                axis = Axis), name = param_layer_name)
        
    
    ########################
    # Segmentation Widgets #
    ########################
    
    @magicgui(
        Range = {"widget_type": "RangeSlider", "min": 0, "max": 255},
        call_button = "Segment")
    def manual_threshold_widget(self,
        Image: napari.layers.Image,
        Preview: bool = False,
        Range = (0, 255)) -> None:
        
        param_layer_name = get_param_layer_name("Manual Threshold", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Min": min(Range),
             "Max": max(Range)})
        self.viewer.add_image(thresh.gui_threshold(Image.data, Range), name = param_layer_name)
        
    @magicgui(
        Method = {"choices": ["Connectivity", "Watershed"]},
        Connectivity = {"choices": [1, 2, 3]},
        Axis = {"choices": ["X", "Y", "Z"]},
        call_button = "Label Segmentation")
    def label_widget(self,
        Image: napari.layers.Image,
        Method: str = "Connectivity",
        Connectivity: int = 3,
        Watershed_Radius: int = 3,
        Watershed_Compactness: float = 0,
        Background: int = 0,
        Along_Axis: bool = False,
        Axis: str = "Z",
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None) -> None:
        
        if not Apply_Mask:
            
            mask_name = None
            mask_array = None
            
        else:
            
            mask_name = Mask.name
            mask_array = Mask.data
            
        if Connectivity > Image.data.ndim:
            
            Connectivity = 2
            
        elif Connectivity > 2 and Along_Axis:
            
            Connectivity = 2
        
        Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)
        
        if Method == "Connectivity":
                
            param_layer_name = get_param_layer_name("Label", self.operation_count)
            self.parameters_log.append(
                {"Name": param_layer_name,
                 "Background": Background,
                 "Connectivity": Connectivity,
                 "Watershed Compactness": Watershed_Compactness,
                 "Along Axis": Along_Axis,
                 "Axis": Axis,
                 "Apply Mask": Apply_Mask,
                 "Mask Used": mask_name})
            
            self.viewer.add_labels(thresh.label(Image.data,
                                                mask_array = mask_array,
                                                connectivity = Connectivity,
                                                background = Background,
                                                positional = Along_Axis,
                                                axis = Axis), name = param_layer_name)
                
        elif Method == "Watershed":
            
            param_layer_name = get_param_layer_name("Watershed", self.operation_count)
            self.parameters_log.append(
                {"Name": param_layer_name,
                 "Background": Background,
                 "Connectivity": Connectivity,
                 "Watershed Radius": Watershed_Radius,
                 "Watershed Compactness": Watershed_Compactness,
                 "Along Axis": Along_Axis,
                 "Axis": Axis,
                 "Apply Mask": Apply_Mask,
                 "Mask Used": Mask.name})
            
            self.viewer.add_labels(detect.watershed(Image.data,
                                                    background = Background,
                                                    mask_array = mask_array,
                                                    connectivity = Connectivity,
                                                    radius = Watershed_Radius,
                                                    compactness = Watershed_Compactness,
                                                    along_axis = Along_Axis,
                                                    axis = Axis), name = param_layer_name)
    
    @magicgui(
        Method = {"choices": ["Isodata", "Li", "Mean", "Minimum", "Otsu", "Triangle", "Yen"]},
        call_button = "Segment")
    def hist_threshold_widget(self,
        Image: napari.layers.Image,
        Method: str = "Otsu",
        Otsu_Classes: int = 2,
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None) -> None:
        
        if not Apply_Mask:
            
            mask_name = None
            mask_array = None
            
        else:
            
            mask_name = Mask.name
            mask_array = Mask.data
        
        param_layer_name = get_param_layer_name("Histogram Threshold", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method.lower(),
             "Otsu Classes": Otsu_Classes,
             "Apply Mask": Apply_Mask,
             "Mask Used": mask_name})
        
        self.viewer.add_image(thresh.hist(Image.data,
                                          method = Method.lower(),
                                          otsu_classes = Otsu_Classes,
                                          mask_array = mask_array),
                              name = param_layer_name)
        
    @magicgui(
        Method = {"choices": ["Adaptive", "Niblack", "Savoula", "Rank"]},
        call_button = "Segment")
    def local_threshold_widget(self,
        Image: napari.layers.Image,
        Method: str = "Adaptive",
        Radius: int = 3,
        Niblack_or_Savoula_Sigma_Weight: float = 0.2,
        Savoula_Sigma_Range: float = 0,
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None) -> None:
        
        if not Apply_Mask:
            
            mask_name = None
            mask_array = None
            
        else:
            
            mask_name = Mask.name
            mask_array = Mask.data
        
        param_layer_name = get_param_layer_name("Local Threshold", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method.lower(),
             "Radius": Radius,
             "Sigma Weight": Niblack_or_Savoula_Sigma_Weight,
             "Sigma Range": Savoula_Sigma_Range,
             "Apply Mask": Apply_Mask,
             "Mask Used": mask_name})
        
        if Savoula_Sigma_Range == 0:
            
            Savoula_Sigma_Range = None
        
        self.viewer.add_image(thresh.local(Image.data,
                                           mask_array = mask_array,
                                           method = Method.lower(),
                                           radius = Radius,
                                           window_size = Radius,
                                           k = Niblack_or_Savoula_Sigma_Weight,
                                           r = Savoula_Sigma_Range), name = param_layer_name)
            
    @magicgui(
        call_button = "Segment")
    def rand_walk_widget(self,
        Image: napari.layers.Image,
        Beta: float = 130,
        Lower_Percentile: float = 5,
        Upper_Percentile: float = 95) -> None:
        
        param_layer_name = get_param_layer_name("Random Walk", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Beta": Beta,
             "Lower Percentile": Lower_Percentile,
             "Upper Percentile": Upper_Percentile})
        self.viewer.add_image(detect.random_walk(Image.data,
                                                 (Lower_Percentile, Upper_Percentile),
                                                 Beta), name = param_layer_name)
    
    @magicgui(
        Method = {"choices": ["ACWE", "GAC"]},
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
        self.parameters_log.append(
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
    
    
    ######################
    # Morphology Widgets #
    ######################
    
    @magicgui(
        Method = {"choices": ["Particles", "Holes"]},
        Connectivity = {"choices": [1, 2, 3]},
        Size_Threshold = {"max": 1000000000},
        Axis = {"choices": ["X", "Y", "Z"]},
        call_button = "Remove Objects")
    def remove_objects_widget(self,
        Image: napari.layers.Image,
        Method: str = "Particles",
        Connectivity: int = 3,
        Size_Threshold: float = 25,
        Background: int = 0,
        Pixel_Scale: float = 1,
        Along_Axis: bool = False,
        Axis: str = "Z") -> None:
        
        if Connectivity > Image.data.ndim:
            
            Connectivity = 2
            
        elif Along_Axis and Connectivity > 2:
            
            Connectivity = 2
            
        Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)            
        param_layer_name = get_param_layer_name("Remove Objects", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method.lower(),
             "Connectivity": Connectivity,
             "Size Threshold": Size_Threshold,
             "Background": Background,
             "Pixel Size": Pixel_Scale,
             "Along Axis": Along_Axis,
             "Axis": Axis})
        self.viewer.add_image(morph.remove_objects(Image.data, Size_Threshold, Method.lower(),
                                                   background = Background,
                                                   pixel_size = Pixel_Scale,
                                                   connectivity = Connectivity,
                                                   along_axis = Along_Axis,
                                                   axis = Axis), name = param_layer_name)
    
    @magicgui(
        call_button = "Dilate")
    def dilate_widget(self,
        Image: napari.layers.Image,
        Iterations: int = 1,
        Along_Z_Axis: bool = False) -> None:
        
        param_layer_name = get_param_layer_name("Dilation", self.operation_count)
        self.parameters_log.append(
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
        self.parameters_log.append(
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
        self.parameters_log.append(
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
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Erosions": Erosions,
             "Dilations": Dilations,
             "Along Axis": Along_Z_Axis})
        self.viewer.add_image(morph.opening(Image.data, Erosions, Dilations, along_axis = Along_Z_Axis), name = param_layer_name)
    
    @magicgui(
        Method = {"choices": ["Black", "White"]},
        call_button = "Top Hat")
    def tophat_widget(self,
        Image: napari.layers.Image,
        Method: str = "Black",
        Dilations: int = 1,
        Erosions: int = 1,
        Along_Z_Axis: bool = False) -> None:
        
        param_layer_name = get_param_layer_name("Top Hat", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method,
             "Dilations": Dilations,
             "Erosions": Erosions,
             "Along Axis": Along_Z_Axis})
        self.viewer.add_image(morph.tophat(Image.data, Method, Dilations, Erosions, along_axis = Along_Z_Axis), name = param_layer_name)
        
    
    ####################
    # Features Widgets #
    ####################
    
    @magicgui(
        Method = {"choices": ["Canny", "Farid", "IGG", "Laplace", "Prewitt", "Roberts", "Scharr", "Sobel"]},
        Edges_Method = {"choices": ["Constant", "Mirror", "Nearest", "Reflect", "Wrap"]},
        Axis = {"choices": ["X", "Y", "Z"]},
        call_button = "Detect Edges")
    def edge_detect_widget(self,
        Image: napari.layers.Image,
        Method: str = "Sobel",
        Edges_Method: str = "Reflect",
        Canny_or_IGG_Sigma: float = 1.0,
        IGG_Alpha: float = 100,
        Laplace_K_Size: int = 3,
        Along_Axis: bool = False,
        Axis: str = "Z") -> None:
        
        Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)
        param_layer_name = get_param_layer_name("Edge Detection", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method.lower(),
             "Edges Method": Edges_Method,
             "Sigma": Canny_or_IGG_Sigma,
             "Alpha": IGG_Alpha,
             "K Size": Laplace_K_Size,
             "Along Axis": Along_Axis,
             "Axis": Axis})
        
        self.viewer.add_image(detect.edge(Image.data,
                                          method = Method.lower(),
                                          sigma = Canny_or_IGG_Sigma,
                                          ksize = Laplace_K_Size,
                                          alpha = IGG_Alpha,
                                          igg_sigma = Canny_or_IGG_Sigma,
                                          along_axis = Along_Axis,
                                          axis = Axis), name = param_layer_name)
    
    @magicgui(
        Method = {"choices": ["Fast", "Harris", "Kitchen Rosenfeld", "Moravec", "Shi Tomasi"]},
        Harris_Method = {"choices": ["K", "Eps"]},
        Return_Mode = {"choices": ["Peaks", "Orientations"]},
        call_button = "Detect Corners")
    def corner_detect_widget(self,
        Image: napari.layers.Image,
        Method: str = "Fast",
        Fast_N: int = 12,
        Fast_Threshold: float = 0.15,
        Harris_Method: str = "K",
        Harris_K: float = 0.05,
        Harris_Epsilon: float = 0.000001,
        Harris_or_Shi_Tomasi_Sigma: float = 1,
        Moravec_Window_Size: int = 1,
        Correct_Anomalies: bool = True,
        Return_Mode: str = "Peaks") -> None:
        
        if Return_Mode == "Peaks":
            
            Return_Mode: str = "peaks array"
            
        elif Return_Mode == "Orientations":
            
            Return_Mode: str = "orients array"
        
        param_layer_name = get_param_layer_name("Corner Detection", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method.lower(),
             "Fast N": Fast_N,
             "Fast Threshold": Fast_Threshold,
             "Harris Method": Harris_Method.lower(),
             "Harris K": Harris_K,
             "Harris Epsilon": Harris_Epsilon,
             "Sigma": Harris_or_Shi_Tomasi_Sigma,
             "Window Size": Moravec_Window_Size,
             "Correct Anomalies": Correct_Anomalies,
             "Return Mode": Return_Mode})
        self.viewer.add_image(detect.corners(Image.data,
                                             method = Method.lower(),
                                             n = Fast_N,
                                             threshold = Fast_Threshold,
                                             harris_method = Harris_Method.lower(),
                                             k = Harris_K,
                                             eps = Harris_Epsilon,
                                             sigma = Harris_or_Shi_Tomasi_Sigma,
                                             window_size = Moravec_Window_Size,
                                             correct_anomalies = Correct_Anomalies,
                                             return_mode = Return_Mode), name = param_layer_name)
        
    @magicgui(
        Method = {"choices": ["Frangi", "Hessian", "Meijering", "Sato"]},
        Edges_Method = {"choices": ["Constant", "Reflect", "Wrap", "Nearest", "Mirror"]},
        call_button = "Detect Ridges")
    def ridge_detect_widget(self,
        Image: napari.layers.Image,
        Method: str = "Frangi",
        Scale_Min: int = 1,
        Scale_Max: int = 10,
        Scale_Step: int = 2,
        Alpha: float = 0.5,
        Beta: float = 0.5,
        Gamma: float = 0,
        Black_Ridges: bool = True,
        Edges_Method: str = "Nearest",
        Constant_Value: float = 0) -> None:
        
        param_layer_name: str = get_param_layer_name("Ridge Detection", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method.lower(),
             "Scale Min": Scale_Min,
             "Scale Max": Scale_Max,
             "Scale_Step": Scale_Step,
             "Alpha": Alpha,
             "Beta": Beta,
             "Gamma": Gamma,
             "Black Ridges": Black_Ridges,
             "Mode": Edges_Method.lower(),
             "Constant Value": Constant_Value})
        
        if Gamma == 0:
            
            Gamma: None = None
        
        self.viewer.add_image(detect.ridges(Image.data,
                                            method = Method.lower(),
                                            scale_range = (Scale_Min, Scale_Max),
                                            scale_step = Scale_Step,
                                            alpha = Alpha,
                                            beta = Beta,
                                            gamma = Gamma,
                                            black_ridges = Black_Ridges,
                                            mode = Edges_Method.lower(),
                                            cval = Constant_Value),
                              name = param_layer_name)
        
    @magicgui(
        Method = {"choices": ["DoG", "DoH", "LoG"]},
        call_button = "Detect Blobs")
    def blob_detect_widget(self,
        Image: napari.layers.Image,
        Method: str = "DoG",
        Min_Sigma: int = 1,
        Max_Sigma: int = 50,
        Sigma_Ratio: float = 1.6,
        Threshold: float = 0.5,
        Overlap: float = 0.5,
        Num_Sigma: int = 10,
        Threshold_Rel: float = 0,
        Exclude_Border: bool = False,
        Log_Scale: bool = False) -> None:
        
        param_layer_name: str = get_param_layer_name("Blob Detection", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method.lower(),
             "Min Sigma": Min_Sigma,
             "Max Sigma": Max_Sigma,
             "Sigma Ratio": Sigma_Ratio,
             "Threshold": Threshold,
             "Overlap": Overlap,
             "Num Sigma": Num_Sigma,
             "Threshold Rel": Threshold_Rel,
             "Exclude Border": Exclude_Border,
             "Log Scale": Log_Scale})
        
        if Threshold_Rel == 0:
            
            Threshold_Rel: None = None
            
        self.viewer.add_image(detect.blobs(Image.data,
                                           method = Method.lower(),
                                           min_sigma = Min_Sigma,
                                           max_sigma = Max_Sigma,
                                           sigma_ratio = Sigma_Ratio,
                                           threshold = Threshold,
                                           overlap = Overlap,
                                           num_sigma = Num_Sigma,
                                           threshold_rel = Threshold_Rel,
                                           exclude_border = Exclude_Border,
                                           log_scale = Log_Scale,
                                           return_mode = "array"),
                              name = param_layer_name)
        
    @magicgui(
        Method = {"choices": ["Lee (2D/3D)", "Zhang (2D)"]},
        call_button = "Detect Skeleton")
    def skeleton_detect_widget(self,
        Image: napari.layers.Image,
        Method: str = "Lee (2D/3D)") -> None:
        
        if Method == "Lee (2D/3D)":
            
            Method: str = "lee"
            
        elif Method == "Zhang (2D)":
            
            Method: str = "zhang"
        
        param_layer_name: str = get_param_layer_name("Skeleton Detection", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Method": Method})
        self.viewer.add_image(detect.skeleton(Image.data, Method), name = param_layer_name)
    
        
    ####################
    # Analysis Widgets #
    ####################
    
    @magicgui(
        X_Max = {"max": 1000000},
        Y_Max = {"max": 1000000000},
        call_button = "Plot Histogram")
    def histogram_widget(self,
        Image: napari.layers.Image,
        Normalize: bool = False,
        Add_CDF: bool = False,
        Remove_Edges: bool = False,
        X_Min: float = 0,
        X_Max: float = 0,
        Y_Max: float = 0,
        Num_Bins: int = 256,
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None,
        Add_as_Parameter: bool = False) -> None:
        
        if not Apply_Mask:
            
            mask_name = None
            mask_array = None
            
        else:
            
            mask_name = Mask.name
            mask_array = Mask.data
        
        if Add_as_Parameter:
            
            param_layer_name = get_param_layer_name("Histogram Plot", self.operation_count)
            self.parameters_log.append(
                {"Name": param_layer_name,
                 "Normalize": Normalize,
                 "Add CDF": Add_CDF,
                 "Remove Edges": Remove_Edges,
                 "X Min": X_Min,
                 "X Max": X_Max,
                 "Y Max": Y_Max,
                 "Num Bins": Num_Bins,
                 "Apply Mask": Apply_Mask,
                 "Mask Used": mask_name})
            
        if Num_Bins == 0:
            
            Num_Bins: None = None
            
        if X_Max == 0:
            
            x_lims = None
            
        else:
            
            x_lims = (X_Min, X_Max)
            
        if Y_Max == 0:
            
            y_lims = None
            
        else:
            
            y_lims = (0, Y_Max)
            
        fig, hist_ax = plt.subplots(layout = "constrained")
        
        hist_ax: plt.Axes = plots.histogram_axis(Image.data,
                                                 hist_ax,
                                                 x_label = "Gray Value",
                                                 mask_array = mask_array,
                                                 xlims = x_lims,
                                                 ylims = y_lims,
                                                 ignore_edges = Remove_Edges,
                                                 normalize = Normalize,
                                                 nbins = Num_Bins)
            
        if Add_CDF:
                
            cdf_ax: plt.Axes = hist_ax.twinx()
            cdf_ax = plots.cdf_axis(Image.data, cdf_ax,
                                    x_label = "Gray Value",
                                    mask_array = Mask.data,
                                    xlims = x_lims)
            cdf_ax.set_ylabel("Probability", rotation = 270, va = "bottom")
                
        plt.show(block = False)
        
    @magicgui(
        call_button = "Plot Line Scan")
    def line_scan_widget(self,
        Image: napari.layers.Image,
        Shapes: napari.layers.Shapes) -> None:
        
        if util.is_3d_rgb(Image.data)["3D"]:
            
            im_array = Image.data[self.viewer.dims.current_step[0]]
            
        else:
            
            im_array = np.copy(Image.data)
            
        _ = plots.gui_line_scan(im_array, Shapes)
            
        plt.show(block = False)
        
    @magicgui(
        call_button = "Plot Gray Level")
    def gray_level_widget(self,
        Image: napari.layers.Image,
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None,
        Add_as_Parameter: bool = False) -> None:
        
        if not Apply_Mask:
            
            mask_name = None
            mask_array = None
            
        else:
            
            mask_name = Mask.name
            mask_array = Mask.data
        
        if Add_as_Parameter:
            
            param_layer_name = get_param_layer_name("Gray Level Plot", self.operation_count)
            self.parameters_log.append(
                {"Name": param_layer_name,
                 "Apply Mask": Apply_Mask,
                 "Mask Used": mask_name})
            
        _ = plots.gray_level(Image.data, mask_array = mask_array)
            
        plt.show(block = False)
        
    @magicgui(
        call_button = "FFT")
    def fft_widget(self,
        Image: napari.layers.Image,
        Along_Z_Axis: bool = False) -> None:
        
        param_layer_name = get_param_layer_name("FFT", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Along Axis": Along_Z_Axis})
        self.viewer.add_image(pixels.convert_im_type(np.real(fourier.ft(Image.data, Along_Z_Axis)), "uint8", norm = True), name = param_layer_name)
        
    @magicgui(
        Method = {"choices": ["Stats", "Percent Intensities", "Total Quantity", "Surface Perimeter/Area", "Contact Perimeter/Area"]},
        Quantity_Measured = {"choices": ["Volume", "Area", "Length"]},
        call_button = "Calculate")
    def misc_calc_widget(self,
        Image: napari.layers.Image,
        Method: str = "Stats",
        Min_Percent: float = 0,
        Max_Percent: float = 100,
        Quantity_Measured: str = "Volume",
        Include_Background: bool = False,
        Background: float = 0,
        Normalize: bool = False,
        Surface_Phase: float = 255,
        Contact_Phase_1: float = 0,
        Contact_Phase_2: float = 255,
        Pixel_Scale: float = 1.0,
        Units: str = "pixels",
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None,
        Add_as_Parameter: bool = False) -> None:
        
        if Apply_Mask:
            
            mask_array: np.ndarray = Mask.data
            mask_name = Mask.name
            
        else:
            
            mask_array = None
            mask_name = None
            
        if Add_as_Parameter:
            
            param_layer_name = get_param_layer_name("Misc Calculations", self.operation_count)
            self.parameters_log.append(
                {"Name": param_layer_name,
                 "Method": Method,
                 "Min Percent": Min_Percent,
                 "Max Percent": Max_Percent,
                 "Quantity Measured": Quantity_Measured,
                 "Include Background": Include_Background,
                 "Background": Background,
                 "Normalize": Normalize,
                 "Surface Phase": Surface_Phase,
                 "Contact Phase 1": Contact_Phase_1,
                 "Contact Phase 2": Contact_Phase_2,
                 "Pixel Size": Pixel_Scale,
                 "Units": Units,
                 "Apply Mask": Apply_Mask,
                 "Mask Used": mask_name})
        
        if Method == "Stats":
            
            _ = quant.global_statistics(Image.data, mask_array = mask_array)
        
        elif Method == "Percent Intensities":
            
            _ = quant.get_percent_intensities(Image.data,
                                              (Min_Percent, Max_Percent),
                                              mask_array = mask_array)
        
        elif Method == "Total Quantity":
            
            if Quantity_Measured == "Volume":
                
                _ = quant.get_volume(Image.data,
                                     mask_array = mask_array,
                                     scale = Pixel_Scale,
                                     units = Units,
                                     include_background = Include_Background,
                                     background = Background,
                                     normalize = Normalize)
                
            elif Quantity_Measured == "Area":
                
                _ = quant.get_area(Image.data,
                                   mask_array = mask_array,
                                   scale = Pixel_Scale,
                                   units = Units,
                                   include_background = Include_Background,
                                   background = Background,
                                   normalize = Normalize)  
                
            elif Quantity_Measured == "Length":
                
                _ = quant.get_length(Image.data,
                                     mask_array = mask_array,
                                     scale = Pixel_Scale,
                                     units = Units,
                                     include_background = Include_Background,
                                     background = Background,
                                     normalize = Normalize)
        
        elif Method == "Surface Perimeter/Area":
            
            _ = quant.get_surface_contact(Image.data, Surface_Phase,
                                          mask_array = mask_array,
                                          pixel_size = Pixel_Scale,
                                          units = Units)

        elif Method == "Contact Perimeter/Area":
            
            _ = quant.get_surface_contact(Image.data, (Contact_Phase_1, Contact_Phase_2),
                                          mask_array = mask_array,
                                          pixel_size = Pixel_Scale,
                                          units = Units)

    @magicgui(
        Type = {"choices": ["Volume", "Area"]},
        Axis = {"choices": ["X", "Y", "Z"]},
        Normalize_Method = {"choices": ["Total", "Phase"]},
        Save_Folder = {"mode": "d"},
        call_button = "Plot Distribution")
    def axis_distribution_widget(self,
        Image: napari.layers.Image,
        Type: str = "Volume",
        Axis: str = "Z",
        Include_Background: bool = False,
        Background: float = 0,
        Pixel_Scale: float = 1,
        Pixel_Units: str = "pixels",
        Normalize: bool = False,
        Normalize_Method: str = "Total",
        Remove_Edges: bool = False,
        X_Min: float = 0,
        X_Max: float = 0,
        Y_Max: float = 0,
        Time_Series: bool = False,
        Time_Units: str = "s",
        Time_Scale: float = 1,
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None,
        Add_as_Parameter: bool = False,
        Export_Data: bool = False,
        Save_Folder: pathlib.Path = pathlib.Path("~"),
        Save_Name: str = "Name") -> None:
        
        if Type == "Volume":
            
            Type = "Vol"
            
        elif Type == "Domain Size":
            
            Type = "Psd"
            
        if not Apply_Mask:
            
            mask_name = None
            mask_array = None
            
        else:
            
            mask_name = Mask.name
            mask_array = Mask.data
            
        Axis: int = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)
        
        if Add_as_Parameter:
            
            param_layer_name = get_param_layer_name("Axis Distribution Plot", self.operation_count)
            self.parameters_log.append(
                {"Name": param_layer_name,
                 "Type": Type.lower(),
                 "Axis": Axis,
                 "Include Background": Include_Background,
                 "Background": Background,
                 "Pixel Size": Pixel_Scale,
                 "Units": Pixel_Units,
                 "Normalize": Normalize,
                 "Normalize Method": Normalize_Method.lower(),
                 "Remove Edges": Remove_Edges,
                 "X Min": X_Min,
                 "X Max": X_Max,
                 "Y Max": Y_Max,
                 "Time Series": Time_Series,
                 "Time Units": Time_Units,
                 "Time Scale": Time_Scale,
                 "Apply Mask": Apply_Mask,
                 "Mask Used": mask_name,
                 "Export Data": Export_Data})
            
        if X_Max == 0:
            
            x_lims = None
            
        else:
            
            x_lims = (X_Min, X_Max)
            
        if Y_Max == 0:
            
            y_lims = None
            
        else:
            
            y_lims = (0, Y_Max)
            
        mode: str = "phase distrib"
        distrib_mode: str = Type.lower()
            
        if Time_Series:
            
            mode: str = "time series"
            
        if not Time_Series:
            
            Time_Units = None
            Time_Scale = None
            
        _, line_df = plots.line(Image.data,
                                mode = mode,
                                distrib_mode = distrib_mode,
                                size_mode = Type.lower(),
                                pixel_size = Pixel_Scale,
                                units = Pixel_Units,
                                mask_array = mask_array,
                                temporal_scale = Time_Scale,
                                temporal_units = Time_Units,
                                axis = Axis,
                                include_background = Include_Background,
                                background = Background,
                                ignore_edges = Remove_Edges,
                                normalize = Normalize,
                                norm_method = Normalize_Method.lower(),
                                xlims = x_lims,
                                ylims = y_lims,
                                return_df = True)
            
        plt.show(block = False)
        
        if Export_Data:
            
            line_df.to_csv(f"{str(Save_Folder)}/{Save_Name}.csv", header = "column names", index = False)
        
    @magicgui(
        Type = {"choices": ["Volume", "Area", "Diameter", "Radius"]},
        Diameter_Radius_Mode = {"choices": ["Volume", "Area"]},
        X_Max = {"max": 1000000},
        Y_Max = {"max": 1000000},
        Max_Bound = {"max": 1000000},
        call_button = "Plot Distribution")
    def psd_widget(self,
        Labels: napari.layers.Labels,
        Type: str = "Volume",
        Diameter_Radius_Mode: str = "Volume",
        Background: int = 0,
        Pixel_Scale: float = 1,
        Units: str = "pixels",
        Normalize: bool = False,
        Remove_Edges: bool = False,
        X_Min: float = 0,
        X_Max: float = 0,
        Y_Max: float = 0,
        Alternate_X_Label: bool = False,
        X_Label: str = None,
        Num_Bins: int = 0,
        Max_Bound: float = 0,
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None,
        Add_as_Parameter: bool = False) -> None:
        
        if Type == "Volume":
            
            Type: str = "vol"
            
        elif Type == "Area":
            
            Type: str = "area"
            
        elif Type == "Diameter":
            
            Type: str = "diam"
            
        elif Type == "Radius":
            
            Type: str = "rad"
            
        if Diameter_Radius_Mode == "Volume":
            
            diam_rad_mode: str = "vol"
            
        elif Diameter_Radius_Mode == "Area":
            
            diam_rad_mode: str = "area"
        
        if not Apply_Mask:
            
            mask_name = None
            mask_array = None
            
        else:
            
            mask_name = Mask.name
            mask_array = Mask.data
            
        if Alternate_X_Label:
            
            x_label: str = X_Label
            
        else:
            
            x_label: None = None
        
        if Add_as_Parameter:
            
            param_layer_name = get_param_layer_name("Domain Size Distribution Plot", self.operation_count)
            self.parameters_log.append(
                {"Name": param_layer_name,
                 "Type": Type,
                 "Diameter Radius Mode": diam_rad_mode,
                 "Background": Background,
                 "Pixel Size": Pixel_Scale,
                 "Units": Units,
                 "Normalize": Normalize,
                 "Remove Edges": Remove_Edges,
                 "X Min": X_Min,
                 "X Max": X_Max,
                 "Y Max": Y_Max,
                 "Alternate X Label": Alternate_X_Label,
                 "X Label": x_label,
                 "Num Bins": Num_Bins,
                 "Max Bound": Max_Bound,
                 "Apply Mask": Apply_Mask,
                 "Mask Used": mask_name})
            
        if X_Max == 0:
            
            x_lims: None = None
            
        else:
            
            x_lims: tuple = (X_Min, X_Max)
            
        if Y_Max == 0:
            
            y_lims: None = None
            
        else:
            
            y_lims: tuple = (0, Y_Max)
            
        if Num_Bins == 0:
            
            Num_Bins: None = None
            
        if Max_Bound == 0:
            
            Max_Bound: None = None
            
        _ = plots.size_distribution(Labels.data,
                                    mode = Type,
                                    diam_rad_mode = diam_rad_mode,
                                    units = Units,
                                    x_label = x_label,
                                    mask_array = mask_array,
                                    xlims = x_lims,
                                    ylims = y_lims,
                                    pixel_size = Pixel_Scale,
                                    normalize = Normalize,
                                    ignore_edges = Remove_Edges,
                                    background = Background,
                                    nbins = Num_Bins,
                                    max_bound = Max_Bound)
            
        plt.show(block = False)
    
    @magicgui(
        Method = {"choices": ["Thickness", "Height"]},
        Color_Map = {"choices": list(colormaps)},
        Height_Direction = {"choices": ["Far", "Near"]},
        Axis = {"choices": ["X", "Y", "Z"]},
        Min_Value = {"max": 1000000},
        Max_Value = {"max": 1000000},
        call_button = "Plot Heat Map")
    def heat_map_widget(self,
        Image: napari.layers.Image,
        Axis: str = "Z",
        Method: str = "Thickness",
        Height_Direction: str = "Near",
        Color_Map: str = "inferno",
        Pixel_Scale: float = 1,
        Units: str = "pixels",
        Define_Limits: bool = False,
        Min_Value: float = 0,
        Max_Value: float = 10,
        Alternate_Colorbar_Label: bool = False,
        Colorbar_Label: str = None,
        Apply_Mask: bool = False,
        Mask: napari.layers.Image = None,
        Return_Array: bool = False,
        Add_as_Parameter: bool = False) -> None:
        
        if not Apply_Mask:
            
            mask_name = None
            mask_array = None
            
        else:
            
            mask_name = Mask.name
            mask_array = Mask.data
            
        if not Alternate_Colorbar_Label:
            
            Colorbar_Label = None
        
        Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Axis)
        param_layer_name = get_param_layer_name("Heat Map", self.operation_count)
        
        if Add_as_Parameter:
            
            self.parameters_log.append(
                {"Name": param_layer_name,
                 "Method": Method.lower(),
                 "Color Map": Color_Map,
                 "Height Direction": Height_Direction,
                 "Axis": Axis,
                 "Pixel Size": Pixel_Scale,
                 "Units": Units,
                 "Define Limits": Define_Limits,
                 "Min Value": Min_Value,
                 "Max Value": Max_Value,
                 "Alternate Colorbar Label": Alternate_Colorbar_Label,
                 "Colorbar Label": Colorbar_Label,
                 "Apply Mask": Apply_Mask,
                 "Mask Used": mask_name,
                 "Return Array": Return_Array})
            
        if Define_Limits:
            
            clim = (Min_Value, Max_Value)
            
        else:
            
            clim = None
            
        if Return_Array:
            
            _, heat_array = plots.heat_map(Image.data,
                                           mode = Method.lower(),
                                           cmap = Color_Map,
                                           clim = clim,
                                           mask_array = mask_array,
                                           pixel_size = Pixel_Scale,
                                           units = Units,
                                           axis = Axis,
                                           height_orientation = Height_Direction.lower(),
                                           cbar_label = Colorbar_Label,
                                           return_array = True)
            self.viewer.add_image(heat_array, name = param_layer_name)
            
        else:
            
            _ = plots.heat_map(Image.data,
                               mode = Method.lower(),
                               cmap = Color_Map,
                               clim = clim,
                               mask_array = mask_array,
                               pixel_size = Pixel_Scale,
                               units = Units,
                               axis = Axis,
                               height_orientation = Height_Direction.lower(),
                               cbar_label = Colorbar_Label)
            
        plt.show(block = False)
        
    
    #####################
    # Visualize Widgets #
    #####################
        
    @magicgui(
        call_button = "Labels to Image")
    def labels_2_image_widget(self,
        Labels: napari.layers.Labels) -> None:
        
        param_layer_name = get_param_layer_name("Labels to Image", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name})
        self.viewer.add_image(pixels.labels_2_rgb(Labels.data), name = param_layer_name)
        
    @magicgui(
        Gradient_Axis = {"choices": ["X", "Y", "Z"]},
        Color_Map = {"choices": list(colormaps)},
        call_button = "Image to Labels")
    def image_2_labels_widget(self,
        Image: napari.layers.Image,
        Gradient: bool = False,
        Gradient_Axis: str = "Z",
        Color_Map: str = "inferno",
        Define_Limits: bool = False,
        Min_Value: float = 0,
        Max_Value: float = 0,
        Pixel_Scale: float = 1,
        Units: str = "pix",
        Colorbar_Label: str = "Position") -> None:
        
        Gradient_Axis = util.convert_ax_str_to_int(Image.data, Image.rgb, Gradient_Axis)
        param_layer_name = get_param_layer_name("Image to Labels", self.operation_count)
        self.parameters_log.append(
            {"Name": param_layer_name,
             "Gradient": Gradient,
             "Gradient Axis": Gradient_Axis,
             "Color Map": Color_Map,
             "Define Limits": Define_Limits,
             "Min Value": Min_Value,
             "Max Value": Max_Value,
             "Pixel Scale": Pixel_Scale,
             "Units": Units,
             "Colorbar Label": Colorbar_Label})
        
        if Gradient:
            
            lab_array: np.ndarray = thresh.create_axial_labels(Image.data, Gradient_Axis)
            
            if Define_Limits:
                
                lab_limits: tuple = (Min_Value, Max_Value)
                
            else:
                
                lab_limits: tuple = ((np.unique(lab_array)[0] * Pixel_Scale), (np.unique(lab_array)[-1] * Pixel_Scale))
            
            cmap, cbar = util.get_colormap(lab_array,
                                           lab_limits = lab_limits, 
                                           cmap = Color_Map,
                                           cbar_scale = Pixel_Scale,
                                           cbar_units = Units,
                                           cbar_label = Colorbar_Label)
            self.viewer.add_labels(lab_array,
                                   colormap = cmap,
                                   opacity = 1,
                                   name = param_layer_name)
            plt.show(block = False)
            
        else:
            
            self.viewer.add_labels(Image.data,
                                   opacity = 1,
                                   name = param_layer_name)
        
        
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

def main() -> napari.viewer.Viewer:
    
    
    # Initialize
    
    viewer: napari.viewer.Viewer = napari.Viewer()
    ui: ImageProcessor = ImageProcessor(viewer)
    tabs: QTabWidget = QTabWidget()
    
    
    # I/O Widgets
    
    mod_im_import: widgets.Container = modify_funcgui(ui.im_import_widget, "Import File")
    mod_dir_import: widgets.Container = modify_funcgui(ui.dir_import_widget, "Import File Sequence")
    mod_im_export: widgets.Container = modify_funcgui(ui.im_export_widget, "Export Image(s)")
    mod_param_export: widgets.Container = modify_funcgui(ui.export_parameters_widget, "Export Parameters")
    mod_lab_export: widgets.Container = modify_funcgui(ui.lab_export_widget, "Export Labels")
    mod_screenshot: widgets.Container = modify_funcgui(ui.screenshot_widget, "Capture Screenshot")
    mod_batch: widgets.Container = modify_funcgui(ui.batch_widget, "Batch Processing")
    io_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_im_import,
                   mod_dir_import,
                   mod_im_export,
                   mod_param_export,
                   mod_lab_export,
                   mod_screenshot,
                   mod_batch],
        labels = False)
    tabs.addTab(io_container.native, "I/O")
    
    
    # Manipulate Widgets
    
    mod_trim_pad: widgets.Container = modify_funcgui(ui.trim_pad_widget, "Trim / Pad")
    mod_crop: widgets.Container = modify_funcgui(ui.crop_widget, "Crop")
    mod_split: widgets.Container = modify_funcgui(ui.split_widget, "Split")
    mod_join: widgets.Container = modify_funcgui(ui.join_widget, "Join")
    mod_extend: widgets.Container = modify_funcgui(ui.extend_widget, "Extend")
    manipulate_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_trim_pad,
                   mod_crop,
                   mod_split,
                   mod_join,
                   mod_extend],
        labels = False)
    tabs.addTab(manipulate_container.native, "Manipulate")
    
    
    # Transform Widgets
    
    mod_reslice: widgets.Container = modify_funcgui(ui.reslice_widget, "Reslice")
    mod_rotate: widgets.Container = modify_funcgui(ui.rotate_widget, "Rotate")
    mod_mirror: widgets.Container = modify_funcgui(ui.mirror_widget, "Mirror")
    mod_resize: widgets.Container = modify_funcgui(ui.resize_widget, "Resize")
    mod_rescale: widgets.Container = modify_funcgui(ui.rescale_widget, "Rescale")
    trans_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_reslice,
                   mod_rotate,
                   mod_mirror,
                   mod_resize,
                   mod_rescale],
        labels = False)
    tabs.addTab(trans_container.native, "Transform")
    
    
    # Masking Widgets
    
    mod_mask: widgets.Container = modify_funcgui(ui.mask_widget, "Mask")
    mod_add_shape: widgets.Container = modify_funcgui(ui.add_shape_widget, "Add Shape")
    mod_create_shape_mask: widgets.Container = modify_funcgui(ui.create_shape_mask_widget, "Create Mask from Shapes")
    mod_paint: widgets.Container = modify_funcgui(ui.paint_widget, "Paint")
    mod_create_paint_mask: widgets.Container = modify_funcgui(ui.create_paint_mask_widget, "Create Mask from Paint")
    mod_mask_logic: widgets.Container = modify_funcgui(ui.mask_logic_widget, "Mask Logic Operations")
    masking_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_mask,
                   mod_add_shape,
                   mod_create_shape_mask,
                   mod_paint,
                   mod_create_paint_mask,
                   mod_mask_logic],
        labels = False)
    tabs.addTab(masking_container.native, "Masking")
    
    
    # Pixel Values Widgets
    
    mod_convert_type: widgets.Container = modify_funcgui(ui.convert_type_widget, "Convert Type")
    mod_normalize: widgets.Container = modify_funcgui(ui.normalize_widget, "Normalize")
    mod_saturate: widgets.Container = modify_funcgui(ui.saturate_widget, "Saturate")
    mod_equalize: widgets.Container = modify_funcgui(ui.equalize_widget, "Equalize Histogram")
    mod_reassign: widgets.Container = modify_funcgui(ui.reassign_widget, "Re-Assign Intensities")
    mod_grayscale: widgets.Container = modify_funcgui(ui.grayscale_widget, "RGB to Grayscale")
    mod_invert: widgets.Container = modify_funcgui(ui.invert_widget, "Invert")
    pixels_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_convert_type,
                   mod_normalize,
                   mod_saturate,
                   mod_equalize,
                   mod_reassign,
                   mod_grayscale,
                   mod_invert],
        labels = False)
    tabs.addTab(pixels_container.native, "Pixel Values")
    
    
    # Denoising Widgets
    
    mod_bilateral: widgets.Container = modify_funcgui(ui.bilateral_widget, "Bilateral Filter")
    mod_gaussian: widgets.Container = modify_funcgui(ui.gaussian_widget, "Gaussian Blur")
    mod_nl_means: widgets.Container = modify_funcgui(ui.nl_means_widget, "Non-Local Means Filter")
    mod_remove_background: widgets.Container = modify_funcgui(ui.remove_background_widget, "Remove Background")
    mod_ring_removal: widgets.Container = modify_funcgui(ui.ring_removal_widget, "Ring Removal")
    mod_tv_bregman: widgets.Container = modify_funcgui(ui.tv_bregman_widget, "TV Bregman Filter")
    mod_tv_chambolle: widgets.Container = modify_funcgui(ui.tv_chambolle_widget, "TV Chambolle Filter")
    mod_wavelet: widgets.Container = modify_funcgui(ui.wavelet_widget, "Wavelet Filter")
    denoising_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_bilateral,
                   mod_gaussian,
                   mod_nl_means,
                   mod_remove_background,
                   mod_ring_removal,
                   mod_tv_bregman,
                   mod_tv_chambolle,
                   mod_wavelet],
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
        widgets = [mod_manual_threshold,
                   mod_label,
                   mod_hist_threshold,
                   mod_local_threshold,
                   mod_rand_walk,
                   mod_morph_snakes],
        labels = False)
    tabs.addTab(segmentation_container.native, "Segmentation")
    
    
    # Morphology Widgets
    
    mod_remove_objects: widgets.Container = modify_funcgui(ui.remove_objects_widget, "Remove Small Objects")
    mod_dilate: widgets.Container = modify_funcgui(ui.dilate_widget, "Dilation")
    mod_erode: widgets.Container = modify_funcgui(ui.erode_widget, "Erosion")
    mod_close: widgets.Container = modify_funcgui(ui.close_widget, "Closing")
    mod_open: widgets.Container = modify_funcgui(ui.open_widget, "Opening")
    mod_tophat: widgets.Container = modify_funcgui(ui.tophat_widget, "Top Hat")
    morphology_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_remove_objects,
                   mod_dilate,
                   mod_erode,
                   mod_close,
                   mod_open,
                   mod_tophat],
        labels = False)
    tabs.addTab(morphology_container.native, "Morphology")
    
    
    # Features Widgets
    
    mod_edge_detect: widgets.Container = modify_funcgui(ui.edge_detect_widget, "Edge Detection")
    mod_corner_detect: widgets.Container = modify_funcgui(ui.corner_detect_widget, "Corner Detection")
    mod_ridge_detect: widgets.Container = modify_funcgui(ui.ridge_detect_widget, "Ridge Detection")
    mod_blob_detect: widgets.Container = modify_funcgui(ui.blob_detect_widget, "Blob Detection")
    mod_skeleton_detect: widgets.Container = modify_funcgui(ui.skeleton_detect_widget, "Skeleton Detection")
    feature_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_edge_detect,
                   mod_corner_detect,
                   mod_ridge_detect,
                   mod_blob_detect,
                   mod_skeleton_detect],
        labels = False)
    tabs.addTab(feature_container.native, "Features")
    
    
    # Analysis Widgets
    
    mod_histogram: widgets.Container = modify_funcgui(ui.histogram_widget, "Histogram")
    mod_line_scan: widgets.Container = modify_funcgui(ui.line_scan_widget, "Line Scan")
    mod_gray_level: widgets.Container = modify_funcgui(ui.gray_level_widget, "Gray Level")
    mod_fft: widgets.Container = modify_funcgui(ui.fft_widget, "FFT")
    mod_misc_calc: widgets.Container = modify_funcgui(ui.misc_calc_widget, "Misc Calculations")
    mod_axis_distribution: widgets.Container = modify_funcgui(ui.axis_distribution_widget, "Axial Distributions")
    mod_psd: widgets.Container = modify_funcgui(ui.psd_widget, "Domain Size Distribution")
    mod_heat_map: widgets.Container = modify_funcgui(ui.heat_map_widget, "Heat Maps")
    analysis_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_histogram,
                   mod_line_scan,
                   mod_gray_level,
                   mod_fft,
                   mod_misc_calc,
                   mod_axis_distribution,
                   mod_psd,
                   mod_heat_map],
        labels = False)
    tabs.addTab(analysis_container.native, "Analysis")
    
    
    # Visualize Widgets
    
    mod_labels_2_image: widgets.Container = modify_funcgui(ui.labels_2_image_widget, "Labels to Image")
    mod_image_2_labels: widgets.Container = modify_funcgui(ui.image_2_labels_widget, "Image to Labels")
    visualize_container: mcw.ScrollableContainer = mcw.ScrollableContainer(
        widgets = [mod_labels_2_image,
                   mod_image_2_labels],
        labels = False)
    tabs.addTab(visualize_container.native, "Visualize")
    
    
    # Launch
    
    tabs.setCurrentIndex(0)
    viewer.window.add_dock_widget(tabs, name = "Image Processing Tools " + version_str)
    napari.run()
    
    return viewer
    
if __name__ == "__main__":
    
    main()