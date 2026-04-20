"""
Module for generating plots to analyze images
"""


# Imports

import pandas as pd
import numpy as np
import napari
import math

from matplotlib import colorbar as cbar, pyplot as plt, transforms as tr
from typing import Callable

from PyDoug.analyze import distrib, quant
from PyDoug.ui import sliceview as sv
from PyDoug.proc import util


# Globals

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"
label_fontsize = 15
tick_fontsize = 13
legend_fontsize = 12


# Functions

def get_basic_colors() -> list[np.ndarray]:
    
    return (np.array([0, 0, 1]),
            np.array([0, 0.5, 0]),
            np.array([1, 0, 0]),
            np.array([0, 0.75, 0.75]),
            np.array([0.75, 0, 0.75]),
            np.array([0.75, 0.75, 0]),
            np.array([0, 0, 0]),
            np.array([0.5, 0.5, 0.5]))

def get_color_list(mode: str = "br", num_colors: int = 2) -> list[np.ndarray]:
    
    color_list: list[tuple] = []
    
    if num_colors == 1:
        
        mode = mode[0]
    
    if mode == "b":
        
        color_base: np.ndarray = np.array([0.121, 0.465, 0.703])
        color_inc: np.ndarray = np.array([0, 0, 0])
        
    elif mode == "r":
        
        color_base = np.array([0.703, 0.047, 0.047])
        color_inc: np.ndarray = np.array([0, 0, 0])
    
    elif mode == "br":
        
        color_base: np.ndarray = np.array([0.121, 0.465, 0.703])
        color_final: np.ndarray = np.array([0.703, 0.047, 0.047])
        color_inc: np.ndarray = (color_final - color_base) / (num_colors - 1)
    
    for index in range(0, num_colors):
        
        if index == 0:
            
            color_list.append(tuple(color_base))
            
        else:
            
            color_list.append(tuple(color_base + (index * color_inc)))
            
    return color_list

def remove_edges(data_df: pd.DataFrame) -> pd.DataFrame:
    
    data_df = data_df[1:-1].reset_index(drop = True)
    eval_array: np.ndarray = np.array(data_df[data_df.columns[1:]]) != 0
    new_start: int = 0
    new_end: int = 0
    
    for col_index in range(0, eval_array.shape[1]):
        
        cur_start: int = util.quick_get_first_index(eval_array[:, col_index])
        
        if cur_start == None:
            
            continue
        
        else:
            
            cur_end: int = eval_array.shape[0] - util.quick_get_first_index(np.flip(eval_array[:, col_index]))
        
        if col_index == 0:
            
            new_start = cur_start
            new_end = cur_end
            
        if cur_start < new_start:
            
            new_start = cur_start
            
        if cur_end > new_end:
            
            new_end = cur_end
    
    return data_df[new_start: new_end].reset_index(drop = True)

def subplot_layout(num_plots: int) -> tuple:
    
    if num_plots == 1:
        
        return (1, 1)
    
    elif num_plots == 2:
        
        return (1, 2)
    
    elif num_plots == 3:
        
        return (1, 3)
    
    elif num_plots == 4:
        
        return (2, 2)
    
    elif num_plots == 5 or num_plots == 6:
        
        return (2, 3)
    
    elif num_plots == 7 or num_plots == 8 or num_plots == 9:
        
        return (3, 3)

def set_axlims(axis: plt.Axes, data_type: np.dtype, y_or_x: str = "x", *, axlims: tuple = None) -> plt.Axes:
    
    if axlims:
        
        if y_or_x == "x":
            
            axis.set_xbound(min(axlims), max(axlims))
        
        elif y_or_x == "y":
            
            axis.set_ybound(min(axlims), max(axlims))
        
    else:
        
        if data_type == "uint8":
            
            if y_or_x == "x":
                
                axis.set_xlim(0, 255)
            
            elif y_or_x == "y":
                
                axis.set_ylim(0, 255)
        
        elif data_type == "uint16":
            
            if y_or_x == "x":
                
                axis.set_xlim(0, 65535)
            
            elif y_or_x == "y":
                
                axis.set_ylim(0, 65535)
                
    return axis

def get_log_starts_widths(log_ax_values: np.ndarray, *,
                          points_per_value: int = 1,
                          point_count_index: int = 0,
                          width: float = 1) -> np.ndarray:
    
    offset_starts: np.ndarray = np.zeros((points_per_value, log_ax_values.shape[0]))
    widths: np.ndarray = np.copy(offset_starts)
    offset_indices: np.ndarray = np.arange(0, points_per_value)
    offset_indices = offset_indices - math.floor((points_per_value / 2))
    
    for index, value in enumerate(log_ax_values):
        
        log_left: np.ndarray = np.logspace(math.log10(value) - 1, math.log10(value), max(round(10 / width), points_per_value))
        log_right: np.ndarray = np.logspace(math.log10(value), math.log10(value) + 1, max(round(10 / width), points_per_value))
        log_range: np.ndarray = np.concat((log_left, log_right[1:]))
        
        for point_index in range(point_count_index, points_per_value):
            
            offset_starts[point_index, index] = log_range[(max(round(10 / width), points_per_value) - 1) + offset_indices[point_index]]
            widths[point_index, index] = log_range[(max(round(10 / width), points_per_value) - 1) + offset_indices[point_index] + 1] - log_range[(max(round(10 / width), points_per_value) - 1) + offset_indices[point_index]]
    
    return offset_starts, widths

def bar_axis(x: np.ndarray, y: np.ndarray, input_ax: plt.Axes = None, *,
             x_labels: tuple[str] = None,
             y_label: str = "Values",
             x_label: str = "Categories",
             y_units: str = None,
             x_units: str = None,
             width: float = 1,
             labels: tuple[str] = None,
             label_index: int = 0,
             y_count: int = 1,
             y_count_index: int = 0,
             ymax: float = None,
             xlims: tuple[float] = None,
             colors: tuple | np.ndarray | str = None,
             color_grad: bool = False,
             add_lines: bool | tuple[bool] = False,
             logx: bool = False,
             logy: bool = False,
             second_axis: bool = False,
             edges: bool = True,
             sci: bool = False) -> plt.Axes:
    
    if edges:
        
        line_width: float = 1
        
    else:
        
        line_width: float = 0
    
    if not second_axis:
        
        if x_units == "um":
            
            x_units = "\u00b5m"
            
        if x_units:
            
            x_title: str = f"{x_label} ({x_units})"
            
        else:
            
            x_title: str = x_label
        
    if y_units == "um":
        
        y_units = "\u00b5m"
        
    if y_units:
        
        y_title: str = f"{y_label} ({y_units})"
        
    else:
        
        y_title: str = y_label
        
    bar_ax: plt.Axes = input_ax
    
    if y_count > 1:
        
        if logx:
            
            offset_starts, widths = get_log_starts_widths(x, points_per_value = y_count,
                                                          point_count_index = y_count_index,
                                                          width = width)
            
            if y_count % 2 != 0:
                        
                align: str = "center"
                    
            else:
                        
                align: str = "edge"
            
        else:
        
            if y_count % 2 != 0:
                
                offset_start: float = -math.floor(y_count / 2) * width
                
            else:
                
                offset_start: float = (-math.floor(y_count / 2) * width) / 2
                
            offset_incs: np.ndarray = np.arange(offset_start, offset_start + (y_count * width), width)
            
        if y.ndim > 1:
            
            range_end: int = y.shape[0]
            
        else:
            
            range_end: int = 1

        for y_index in range(0, range_end):
            
            if y.ndim > 1:
                
                cur_y: np.ndarray = y[y_index, :]
                
            else:
                
                cur_y: np.ndarray = y
            
            if colors is not None:
                
                if isinstance(colors, tuple):
                
                    color = colors[y_index]
                    
                else:
                    
                    color = colors
                
            else:
                
                color = get_basic_colors()[y_index]
                
            if logx:
                                
                if labels:
                
                    bar_ax.bar(offset_starts[y_index + (y_count_index * second_axis), :],
                               cur_y,
                               width = widths[y_index + (y_count_index * second_axis), :],
                               color = color,
                               label = labels[label_index],
                               align = align,
                               linewidth = line_width,
                               edgecolor = "k",
                               tick_label = x_labels)
                    label_index += 1
                    
                else:
                    
                    bar_ax.bar(offset_starts[y_index + (y_count_index * second_axis), :],
                               cur_y,
                               width = widths[y_index + (y_count_index * second_axis), :],
                               color = color,
                               align = align,
                               linewidth = line_width,
                               edgecolor = "k",
                               tick_label = x_labels)
            
            else:
                
                if labels:
                
                    bar_ax.bar(x + offset_incs[y_index + (y_count_index * second_axis)],
                               cur_y,
                               width = width,
                               color = color,
                               label = labels[label_index],
                               linewidth = line_width,
                               edgecolor = "k",
                               tick_label = x_labels)
                    label_index += 1
                    
                else:
                    
                    bar_ax.bar(x + offset_incs[y_index + (y_count_index * second_axis)],
                               cur_y,
                               width = width,
                               color = color,
                               linewidth = line_width,
                               edgecolor = "k",
                               tick_label = x_labels)
                
            if add_lines:
                
                if isinstance(add_lines, tuple):
                    
                    if add_lines[y_index]:
                        
                        plot_line: bool = True
                            
                    else:
                        
                        plot_line: bool = False
        
                else:
                    
                    plot_line: bool = True
                    
            else:
                
                plot_line: bool = False
                
            if plot_line:
                    
                if logx:
                    
                    if y_count % 2 != 0:
                        
                        bar_ax.plot(offset_starts[y_index + (y_count_index * second_axis), :], cur_y, color = color / 2)
                        
                    else:
                        
                        line_offset_starts: np.ndarray = np.zeros(offset_starts.shape[1])
                        
                        for index, offset in enumerate(offset_starts[y_index + (y_count_index * second_axis), :]):
                            
                            line_offset_starts[index] = offset + np.diff(np.logspace(math.log10(offset), math.log10(offset + widths[y_index + (y_count_index * second_axis), index]), 3))[0]
                        
                        bar_ax.plot(line_offset_starts, cur_y, color = color / 2)
                    
                else:
                
                    bar_ax.plot(x + offset_incs[y_index], cur_y, color = color / 2)
    
    else:
        
        if logx:
            
            _, widths = get_log_starts_widths(x, width = width)
            widths = np.squeeze(widths)
                
        else:
            
            widths = np.repeat(width, x.shape[0])
            
        if color_grad:
            
            num_grads: int = len(colors) - 1
            
            if logx:
                
                range_markers: np.ndarray = np.astype(np.round(np.logspace(math.log10(1), math.log10(x.shape[0] + 1), (num_grads + 1))), np.int64)
                
            else:
                
                range_markers: np.ndarray = np.astype(np.round(np.linspace(0, x.shape[0], (num_grads + 1))), np.int64)
            
            for index in range(0, num_grads):
                
                cur_start: np.ndarray = colors[index]
                cur_end: np.ndarray = colors[index + 1]
                cur_range: int = range_markers[index + 1] - range_markers[index]
                
                if index != 0:
                    
                    cur_range += 1
            
                cur_grad_colors: np.ndarray = np.concat((np.expand_dims((np.linspace(cur_start[0], cur_end[0], cur_range)), 1),
                                                         np.expand_dims((np.linspace(cur_start[1], cur_end[1], cur_range)), 1),
                                                         np.expand_dims((np.linspace(cur_start[2], cur_end[2], cur_range)), 1)),
                                                        axis = 1)
                    
                if index == 0:
                    
                    grad_colors: np.ndarray = cur_grad_colors
                    
                else:
                    
                    grad_colors = np.concat((grad_colors, cur_grad_colors[1:, :]), axis = 0)
            
            for index, x_value in enumerate(x):
                
                bar_ax.bar(x_value,
                           y[index],
                           width = widths[index],
                           color = grad_colors[index, :],
                           linewidth = line_width,
                           edgecolor = "k",
                           tick_label = x_labels)
                
        else:
                
            if labels:
                    
                bar_ax.bar(x,
                           y,
                           width = widths,
                           color = colors,
                           label = labels[label_index],
                           linewidth = line_width,
                           edgecolor = "k",
                           tick_label = x_labels)
                    
            else:
                    
                bar_ax.bar(x,
                           y,
                           width = widths, 
                           color = colors,
                           linewidth = line_width,
                           edgecolor = "k",
                           tick_label = x_labels)
        
            if add_lines:
                
                bar_ax.plot(x, y, color = colors / 2)
    
    bar_ax.set_ylabel(y_title, fontsize = label_fontsize)
    
    if not second_axis:
        
        bar_ax.set_xlabel(x_title, fontsize = label_fontsize)
        
    else:
        
        bar_ax.set_ylabel(y_title, rotation = 270, va = "bottom", fontsize = label_fontsize)
        
    if logx:
        
        bar_ax.set_xscale("log")
        
        if xlims:
            
            bar_ax.set_xlim(min(xlims), max(xlims))
            
    else:
        
        if xlims:
            
            bar_ax.set_xlim(min(xlims), max(xlims))
        
    if logy:
        
        bar_ax.set_yscale("log")
        
        if ymax:
            
            bar_ax.set_ylim(0, ymax)
            
    else:
        
        if ymax:
            
            bar_ax.set_ylim(0, ymax)
            
    if sci:
        
        bar_ax.ticklabel_format(axis = "y", style = "sci", scilimits = (0, 0))
        
    bar_ax.tick_params(axis = "both", labelsize = tick_fontsize)
    
    return bar_ax, label_index

def simple_bar(x: np.ndarray, y: np.ndarray, *,
               x_labels: tuple[str] = None,
               y_label: str = "Values",
               x_label: str = "Categories",
               y_units: str = None,
               x_units: str = None,
               width: float = 1,
               labels: tuple[str] = None,
               ymax: float = None,
               xlims: tuple[float] = None,
               colors: tuple | np.ndarray | str = None,
               color_grad: bool = False,
               add_lines: bool | tuple[bool] = False,
               logx: bool = False,
               logy: bool = False,
               sci: bool = False,
               axis2: bool = False,
               y2: np.ndarray = None,
               y2_label: str = "Values",
               y2_units: str = None,
               y2max: float = None,
               colors2: tuple = None,
               add_lines2: bool = False,
               logy2: bool = False,
               legend_axis: int = 2,
               edges: bool = True,
               sci2: bool = False,
               dx: float = 0) -> plt.Figure:
    
    if y.ndim > 1:
        
        y_count: int = y.shape[0]
        
    else:
        
        y_count: int = 1
    
    if axis2:
        
        if y2.ndim > 1:
        
            y_count += y2.shape[0]
            
        else:
            
            y_count += 1
        
    fig, bar_ax = plt.subplots(layout = "constrained")
    bar_ax, label_index = bar_axis(x, y, bar_ax,
                                   x_labels = x_labels,
                                   y_label = y_label,
                                   x_label = x_label,
                                   y_units = y_units,
                                   x_units = x_units,
                                   width = width,
                                   labels = labels,
                                   y_count = y_count,
                                   y_count_index = 0,
                                   ymax = ymax,
                                   xlims = xlims,
                                   colors = colors,
                                   color_grad = color_grad,
                                   add_lines = add_lines,
                                   logx = logx,
                                   logy = logy,
                                   edges = edges,
                                   sci = sci)
    
    if axis2:
        
        bar_ax2 = bar_ax.twinx()
        
        if y.ndim > 1:
            
            y_count_index: int = y.shape[0]
            
        else:
            
            y_count_index: int = 1
        
        bar_ax2, _ = bar_axis(x, y2, bar_ax2,
                              x_labels = x_labels,
                              y_label = y2_label,
                              y_units = y2_units,
                              width = width,
                              labels = labels,
                              label_index = label_index,
                              y_count = y_count,
                              y_count_index = y_count_index,
                              ymax = y2max,
                              xlims = xlims,
                              colors = colors2,
                              add_lines = add_lines2,
                              logx = logx,
                              logy = logy2,
                              second_axis = axis2,
                              edges = edges,
                              sci = sci2)
        
    if x_labels:
        
        dy: float = 0
        bar_ax.tick_params(axis = "x", length = 0, labelsize = tick_fontsize)
        offset: tr.ScaledTranslation = tr.ScaledTranslation(dx, dy, fig.dpi_scale_trans)
        
        for label, line in zip(bar_ax.xaxis.get_majorticklabels(), bar_ax.xaxis.get_majorticklines()):
            
            label.set_transform(label.get_transform() + offset)
            #line.set_transform(line.get_transform() + offset)
        
    if labels:
        
        bars, bars_labels = bar_ax.get_legend_handles_labels()
        
        if axis2:
            
            bars2, bars_labels2 = bar_ax2.get_legend_handles_labels()
            
            if legend_axis == 2:
                
                bar_ax2.legend(bars + bars2, bars_labels + bars_labels2, frameon = False, fontsize = legend_fontsize)
                
            else:
                
                bar_ax.legend(bars + bars2, bars_labels + bars_labels2, frameon = False, fontsize = legend_fontsize)
            
        else:
            
            bar_ax.legend(bars, bars_labels, frameon = False, fontsize = legend_fontsize)
    
    return fig

def box_whisker(data: np.ndarray | tuple[np.ndarray], *,
                categories: list | tuple | np.ndarray = None,
                cat_label: str = "Categories",
                cat_units: str = None,
                data_label: str = "Values",
                data_units: str = None,
                orientation: str = "vertical",
                widths: float = 0.5,
                data_lims: tuple = None,
                colors: np.ndarray = None) -> plt.Figure:
    
    if cat_units:
        
        if cat_units == "um":
            
            cat_units = "\u00b5m"
        
        cat_label = f"{cat_label} ({cat_units})"
        
    if data_units:
        
        if data_units == "um":
            
            data_units = "\u00b5m"
        
        data_label = f"{data_label} ({data_units})"
        
    fig, box_ax = plt.subplots(layout = "constrained")
    bp = box_ax.boxplot(data, orientation = orientation,
                        tick_labels = categories,
                        widths = widths,
                        patch_artist = True)
    
    if orientation == "vertical":
        
        box_ax.set_xlabel(cat_label, fontsize = label_fontsize)
        box_ax.set_ylabel(data_label, fontsize = label_fontsize)
        
        if data_lims:
            
            box_ax.set_ylim(min(data_lims), max(data_lims))
        
    else:
        
        box_ax.set_ylabel(cat_label, fontsize = label_fontsize)
        box_ax.set_xlabel(data_label, fontsize = label_fontsize)
        
        if data_lims:
            
            box_ax.set_xlim(min(data_lims), max(data_lims))
            
    for median in bp["medians"]:
        
        median.set(color = "black")
        
    if np.any(colors):
        
        for index, patch in enumerate(bp["boxes"]):
            
            if isinstance(colors, np.ndarray):
                
                if colors.ndim == 1:
                
                    patch.set_facecolor(colors)
                
                else:
                
                    patch.set_facecolor(colors[index, :])
                    
            elif isinstance(colors, tuple):
                
                patch.set_facecolor(colors[index])
                
    box_ax.tick_params(axis = "both", labelsize = tick_fontsize)
        
    return fig

def line_axis(data: np.ndarray | pd.DataFrame = None,
              input_ax: plt.Axes = None,
              mode: str = "line scan", *,
              color_mode: str = "br",
              viewer: napari.viewer.Viewer = None,
              slice_range: tuple[int] = None,
              distrib_mode: str = "vol",
              size_mode: str = "area",
              pixel_size: float = 1.0,
              units: str = "pix",
              mask_array: np.ndarray = None,
              temporal_scale: float | int = None,
              temporal_units: str = "s",
              axis: int = 0,
              include_background: bool = False,
              background: float | int = 0,
              ignore_edges: bool = False,
              connectivity: int = None,
              normalize: bool = False,
              norm_method: str = "total",
              xlims: tuple = None,
              ylims: tuple = None,
              return_df: bool = False) -> plt.Axes:
    
    if not isinstance(data, pd.DataFrame):
        
        if mode == "line scan":
            
            line_df: pd.DataFrame = sv.quick_get_line_scan(viewer,
                                                           slice_range,
                                                           pixel_size = pixel_size,
                                                           units = units)
        
        elif mode == "phase distrib":
            
            line_df: pd.DataFrame = distrib.get_position_distribution(data,
                                                                      mode = distrib_mode,
                                                                      mask_array = mask_array,
                                                                      pixel_size = pixel_size,
                                                                      units = units,
                                                                      axis = axis,
                                                                      include_background = include_background,
                                                                      background = background,
                                                                      normalize = normalize,
                                                                      norm_method = norm_method)
        
        elif mode == "psd distrib":
            
            line_df: pd.DataFrame = distrib.get_size_distribution(data,
                                                                  mask_array = mask_array,
                                                                  mode = distrib_mode,
                                                                  pixel_size = pixel_size,
                                                                  units = units,
                                                                  connectivity = connectivity,
                                                                  background = background,
                                                                  normalize = normalize,
                                                                  positional = True,
                                                                  temporal_scale = temporal_scale,
                                                                  temporal_units = temporal_units)
            
        elif mode == "time series":
            
            line_df: pd.DataFrame = distrib.get_time_series(data,
                                                            mode = distrib_mode,
                                                            size_mode = size_mode,
                                                            mask_array = mask_array,
                                                            pixel_size = pixel_size,
                                                            spatial_units = units,
                                                            temporal_scale = temporal_scale,
                                                            temporal_units = temporal_units,
                                                            connectivity = connectivity,
                                                            background = background,
                                                            include_background = include_background,
                                                            normalize = normalize,
                                                            norm_method = norm_method)
            
    else:
        
        line_df: pd.DataFrame = data.copy()
        
    if mode == "phase distrib" or mode == "line scan":
        
        x_units: str = line_df.attrs["pos_units"]
        x_label: str = f"Position ({x_units})"
        
    elif mode == "psd distrib":
        
        if size_mode == "vol":
            
            x_units: str = line_df.attrs["vol_units"]
            x_label = f"Volume ({x_units})"
            
        elif size_mode == "area":
            
            x_units: str = line_df.attrs["area_units"]
            x_label = f"Area ({x_units})"
            
        elif size_mode == "diam":
            
            x_units: str = line_df.attrs["diam_units"]
            x_label == f"Diameter ({x_units})"
        
    elif mode == "time series":
        
        
        if distrib_mode != "size":
            
            x_units: str = line_df.attrs["time_units"]
            x_label: str = f"Time ({x_units})"
            
        else:
            
            if size_mode == "vol":
                
                x_units: str = line_df.attrs["vol_units"]
                x_label = f"Volume ({x_units})"
                
            elif size_mode == "area":
                
                x_units: str = line_df.attrs["area_units"]
                x_label = f"Area ({x_units})"
                
            elif size_mode == "diam":
                
                x_units: str = line_df.attrs["diam_units"]
                x_label == f"Diameter ({x_units})"
        
    if normalize:
        
        if mode == "phase distrib" or mode == "time series":
        
            if distrib_mode == "vol":
            
                y_label: str = "Volumetric Probability Density"
                
            elif distrib_mode == "area":
                
                y_label: str = "Areal Probability Density"
                
            elif distrib_mode == "diam":
                
                y_label: str = "Size Probability Density"
                
            elif distrib_mode == "size":
                
                y_label: str = "Probability Density"
                
        elif mode == "psd distrib":
            
            y_label: str = "Probability Density"
        
    else:
        
        if mode == "line scan":
            
            y_label: str = "Gray Value"
            
        elif mode == "phase distrib" or mode == "time series":
            
            if distrib_mode == "vol":
                
                y_units: str = line_df.attrs["vol_units"]
                y_label: str = f"Volume ({y_units})"
                
            elif distrib_mode == "area":
                
                y_units: str = line_df.attrs["area_units"]
                y_label: str = f"Area ({y_units})"
                
            elif distrib_mode == "diam":
                
                y_units: str = line_df.attrs["diam_units"]
                y_label: str = f"Diameter ({y_units})"
                
            elif distrib_mode == "size":
                
                y_label: str = "Counts"
                
        else:
            
            y_label: str = "Counts"
        
    if ignore_edges:
        
        line_df = remove_edges(line_df)
        
    line_ax: plt.Axes = input_ax
    color_list: list[np.ndarray] = get_color_list(color_mode, len(line_df.columns) - 1)
    
    for index, column in enumerate(line_df.columns):
        
        if index == 0:
            
            x_values: pd.Series = line_df[column]
            
        else:
            
            line_ax.plot(x_values, line_df[column], color = color_list[index - 1])
    
    line_ax.set_xlabel(x_label, fontsize = label_fontsize)
    line_ax.set_ylabel(y_label, fontsize = label_fontsize)
    
    if xlims:
        
        line_ax.set_xlim(min(xlims), max(xlims))
        
    else:
        
        line_ax.set_xlim(0)
    
    if ylims:
        
        line_ax.set_ylim(min(ylims), max(ylims))
        
    else:
        
        line_ax.set_ylim(0)
        
    line_ax.tick_params(axis = "both", labelsize = tick_fontsize)
        
    if return_df:
        
        return line_ax, line_df
    
    else:
        
        return line_ax

def line(data: np.ndarray | pd.DataFrame,
         mode: str = "line scan", *,
         color_mode: str = "br",
         viewer: napari.viewer.Viewer = None,
         slice_range: tuple[int] = None,
         distrib_mode: str = "vol",
         size_mode: str = "area",
         pixel_size: float = 1.0,
         units: str = "pix",
         mask_array: np.ndarray = None,
         temporal_scale: float | int = None,
         temporal_units: str = "s",
         axis: int = 0,
         include_background: bool = False,
         background: float | int = 0,
         connectivity: int = None,
         ignore_edges: bool = False,
         normalize: bool = False,
         norm_method: str = "total",
         xlims: tuple = None,
         ylims: tuple = None,
         return_df: bool = False) -> plt.Figure:
    
    # if mode == "psd distrib":
        
    #     c_label: str = f"Thickness ({units})"
        
    # elif mode == "time series":
        
    #     c_label: str = f"Height ({units})"
    
    fig, line_ax = plt.subplots(layout = "constrained")
    
    line_ax, line_df = line_axis(data,
                                 line_ax,
                                 mode = mode,
                                 color_mode = color_mode,
                                 viewer = viewer,
                                 slice_range = slice_range,
                                 distrib_mode = distrib_mode,
                                 size_mode = size_mode,
                                 pixel_size = pixel_size,
                                 units = units,
                                 mask_array = mask_array,
                                 temporal_scale = temporal_scale,
                                 temporal_units = temporal_units,
                                 axis = axis,
                                 include_background = include_background,
                                 background = background,
                                 connectivity = connectivity,
                                 ignore_edges = ignore_edges,
                                 normalize = normalize,
                                 norm_method = norm_method,
                                 xlims = xlims,
                                 ylims = ylims,
                                 return_df = True)
        
    # fig_cbar: cbar.Colorbar = fig.colorbar(ax_im)
    # fig_cbar.set_label(c_label, rotation = 270, va = "bottom")
    
    if return_df:
        
        return fig, line_df
    
    else:
        
        return fig

def gui_line_scan(im_array: np.ndarray, shapes_layer: napari.layers.Shapes) -> plt.Figure:
    
    line_scan_df: pd.DataFrame = sv.quick_get_line_scan(im_array = im_array, shapes_layer = shapes_layer)
    fig, ls_ax = plt.subplots(layout = "constrained")
    ls_ax.set_xlabel("Position [pix]", fontsize = label_fontsize)
    ls_ax.set_ylabel("Gray Value", fontsize = label_fontsize)
    ls_ax.plot(line_scan_df["Position"], line_scan_df["Gray Value"], "red")
    ls_ax.set_xlim(0, line_scan_df["Position"][len(line_scan_df["Position"]) - 1])
    ls_ax.tick_params(axis = "both", labelsize = tick_fontsize)
    
    return fig

def histogram_axis(
        data: np.ndarray | pd.DataFrame,
        input_ax: plt.Axes, *,
        x_label: str = "Value",
        mask_array: np.ndarray = None,
        xlims: tuple = None,
        ylims: tuple = None,
        units: str = None,
        ignore_edges: bool = False,
        normalize: bool = False,
        nbins: int | None = None,
        max_bound: float | None = None,
        logx: bool = False,
        return_df: bool = False,
        return_stats_df: bool = False) -> plt.Axes:
    
    if not nbins:
        
        nbins: int = 256
    
    if isinstance(data, np.ndarray):
        
        hist_df: pd.DataFrame = distrib.get_histogram(
            data,
            mask_array = mask_array,
            normalize = normalize,
            nbins = nbins,
            max_bound = max_bound)
        
    else:
        
        hist_df: pd.DataFrame = data.copy()
        
    hist_mean: float = np.sum(
        (hist_df["Bin Centers"] * hist_df["Counts"])) / np.sum(hist_df["Counts"])
    print(f"\n{"Histogram Mean:":<16} {hist_mean}")
    
    if not normalize:
        
        ext_bin_centers: np.ndarray = distrib.extend_histogram_bins(
            hist_df["Bin Centers"],
            hist_df["Counts"])            
        hist_std: float = np.std(ext_bin_centers)
        print(f"{"Histogram StDv:":<16} {hist_std}")
        print(f"{"Total Counts:":<16} {np.sum(hist_df["Counts"])}")
        hist_stats_df: pd.DataFrame = pd.DataFrame(
            np.array([[hist_mean, hist_std, np.sum(hist_df["Counts"])]]),
            columns = ["Mean", "Std. Dev.", "Counts"])
        
    else:
        
        hist_stats_df: pd.DataFrame = pd.DataFrame(
            np.array([[hist_mean]]),
            columns = ["Mean"])
        
    if ignore_edges:
        
        hist_df = remove_edges(hist_df)
        
    hist_ax: plt.Axes = input_ax
    hist_ax.set_xlabel(x_label, fontsize = label_fontsize)
    
    if normalize:
        
        hist_ax.set_ylabel("Probability Density", fontsize = label_fontsize)
    
    else:
        
        hist_ax.set_ylabel("Counts", fontsize = label_fontsize)
        
    hist_ax.hist(hist_df["Bin Centers"], hist_df["Bin Centers"], weights = hist_df["Counts"], edgecolor = "k")
    
    if xlims:
        
        hist_ax = set_axlims(hist_ax, hist_df["Bin Centers"].dtype, "x", axlims = xlims)
        
    else:
        
        hist_ax.set_xlim(np.min(hist_df["Bin Centers"]), np.max(hist_df["Bin Centers"]))
        
    if ylims:
        
        hist_ax.set_ylim(min(ylims), max(ylims))
        
    if logx:
        
        hist_ax.set_xscale("log")
        
    hist_ax.tick_params(axis = "both", labelsize = tick_fontsize)
        
    if return_stats_df:
        
        return hist_ax, hist_stats_df
    
    else:
        
        return hist_ax

def histogram(
        data: np.ndarray | pd.DataFrame, *,
        x_label: str = "Value",
        mask_array: np.ndarray = None,
        xlims: tuple = None,
        ylims: tuple = None,
        ignore_edges: bool = False,
        normalize: bool = False,
        nbins: int | None = None,
        logx: bool = False,
        return_df: bool = False,
        return_stats_df: bool = False) -> plt.Figure:
    
    fig, hist_ax = plt.subplots(layout = "constrained")
    hist_ax, hist_stats_df = histogram_axis(
        data, hist_ax,
        x_label = x_label,
        mask_array = mask_array,
        xlims = xlims,
        ylims = ylims,
        ignore_edges = ignore_edges,
        normalize = normalize,
        nbins = nbins,
        logx = logx,
        return_df = False,
        return_stats_df = True)
    
    if return_stats_df:
    
        return fig, hist_stats_df
    
    else:
        
        return fig

def size_distribution_ax(
        data: np.ndarray | pd.DataFrame,
        input_ax: plt.Axes, *,
        mode: str = "vol",
        diam_rad_mode = "vol",
        units: str = "pix",
        mask_array: np.ndarray = None,
        x_label: str = None,
        xlims: tuple = None,
        ylims: tuple = None,
        pixel_size: float = 1.0,
        ignore_edges: bool = False,
        normalize: bool = False,
        connectivity: int = None,
        background: float | int = 0,
        nbins: int = 100,
        max_bound: float | None = None,
        return_df: bool = False) -> plt.Axes:
    
    if isinstance(data, np.ndarray):
        
        psd_df: pd.DataFrame = distrib.get_size_distribution(
            data,
            mask_array = mask_array,
            mode = mode,
            diam_rad_mode = diam_rad_mode,
            pixel_size = pixel_size,
            units = units,
            connectivity = connectivity,
            background = background,
            normalize = normalize,
            nbins = nbins,
            max_bound = max_bound)
    
    else:
        
        psd_df: pd.DataFrame = data.copy()
    
    if x_label:
        
        x_label: str = f"{x_label} ({psd_df.attrs["units"]})"
    
    else:
    
        x_label: str = f"Domain Size ({psd_df.attrs["units"]})"
        
    psd_ax = input_ax
    psd_ax, hist_stats_df = histogram_axis(
        psd_df,
        psd_ax,
        x_label = x_label,
        mask_array = mask_array,
        xlims = xlims,
        ylims = ylims,
        ignore_edges = ignore_edges,
        normalize = normalize,
        nbins = nbins,
        max_bound = max_bound,
        return_stats_df = True)
    psd_ax.tick_params(axis = "both", labelsize = tick_fontsize)
    
    if return_df:
        
        return psd_ax, psd_df, hist_stats_df
    
    else:
        
        return psd_ax

def size_distribution(
        data: np.ndarray | pd.DataFrame, *,
        mode: str = "vol",
        diam_rad_mode: str = "vol",
        units: str = "pix",
        mask_array: np.ndarray = None,
        x_label: str = None,
        xlims: tuple = None,
        ylims: tuple = None,
        pixel_size: float = 1.0,
        ignore_edges: bool = False,
        normalize: bool = False,
        connectivity: int = None,
        background: float | int = 0,
        nbins: int = 100,
        max_bound: float | None = None,
        return_df: bool = False) -> plt.Figure:
    
    fig, psd_ax = plt.subplots(layout = "constrained")
    psd_ax, psd_df, hist_stats_df = size_distribution_ax(
        data, psd_ax,
        mode = mode,
        diam_rad_mode = diam_rad_mode,
        units = units,
        mask_array = mask_array,
        x_label = x_label,
        xlims = xlims,
        ylims = ylims,
        pixel_size = pixel_size,
        ignore_edges = ignore_edges,
        normalize = normalize,
        connectivity = connectivity,
        background = background,
        nbins = nbins,
        max_bound = max_bound,
        return_df = True)
    
    if return_df:
        
        return fig, psd_df, hist_stats_df
    
    else:
        
        return fig

def cdf_axis(data: np.ndarray | pd.DataFrame, input_ax: plt.Axes, *,
             x_label: str = "Value",
             mask_array: np.ndarray = None,
             xlims: tuple = None,
             ylims: tuple = None) -> plt.Axes:
    
    if isinstance(data, np.ndarray):
    
        cdf_df: pd.DataFrame = distrib.get_cdf(data, mask_array = mask_array)
        
    else:
        
        cdf_df: pd.DataFrame = data.copy()
        
    cdf_ax: plt.Axes = input_ax
    cdf_ax.set_xlabel(x_label, fontsize = label_fontsize)
    cdf_ax.set_ylabel("Probability", fontsize = label_fontsize)
    cdf_ax.set_ylim(0, 1)
    cdf_ax.plot(cdf_df["Bin Centers"], cdf_df["Probability"], "red")
    
    if xlims:
        
        cdf_ax = set_axlims(cdf_ax, cdf_df["Bin Centers"].dtype, "x", axlims = xlims)
        
    else:
        
        cdf_ax.set_xlim(np.min(cdf_df["Bin Centers"]), np.max(cdf_df["Bin Centers"]))
        
    if ylims:
        
        cdf_ax.set_ylim(min(ylims), max(ylims))
        
    cdf_ax.tick_params(axis = "both", labelsize = tick_fontsize)
        
    return cdf_ax

def cdf(data: np.ndarray | pd.DataFrame, *,
        x_label: str = "Value",
        mask_array: np.ndarray = None,
        xlims: tuple = None,
        ylims: tuple = None) -> plt.Figure:
    
    fig, cdf_ax = plt.subplots(layout = "constrained")
    cdf_ax = cdf_axis(data, cdf_ax, mask_array = mask_array, xlims = xlims, ylims = ylims)
    
    return fig

def hist_cdf(data: np.ndarray | dict, *,
             x_label: str = "Value",
             mask_array: np.ndarray = None,
             xlims: tuple = None,
             ylims: tuple = None,
             ignore_edges: bool = False,
             normalize: bool = False) -> plt.Figure:
    
    fig, hist_ax = plt.subplots(layout = "constrained")
    hist_ax = histogram_axis(data, hist_ax,
                             x_label = x_label,
                             mask_array = mask_array,
                             xlims = xlims,
                             ylims = ylims,
                             ignore_edges = ignore_edges,
                             normalize = normalize)
    cdf_ax: plt.Axes = hist_ax.twinx()
    cdf_ax.set_ylabel("Probability", rotation = 270, va = "bottom", fontsize = label_fontsize)
    cdf_ax = cdf_axis(data, cdf_ax,
                      x_label = x_label,
                      mask_array = mask_array,
                      xlims = xlims,
                      ylims = ylims)
    
    return fig

def gray_level_axis(data: np.ndarray | pd.DataFrame, input_ax: plt.Axes, quant_axis: int = 0, *,
                    mask_array: np.ndarray = None) -> plt.Axes:
    
    if isinstance(data, np.ndarray):
        
        gray_df: pd.DataFrame = quant.single_ax_statistics(data, quant_axis, mask_array = mask_array)
        
    else:
        
        gray_df: pd.DataFrame = data.copy()
        
    pos_std: np.ndarray = gray_df["Mean"] + gray_df["Std Dev"]
    neg_std: np.ndarray = gray_df["Mean"] - gray_df["Std Dev"]
    gray_ax: plt.Axes = input_ax
    gray_ax.set_xlabel("Position [pixels]", fontsize = label_fontsize)
    gray_ax.set_ylabel("Gray Value", fontsize = label_fontsize)
    gray_ax.set_xlim(0, max(gray_df["Position"]))
    gray_ax.plot(gray_df["Position"], gray_df["Mean"], "black")
    gray_ax.plot(gray_df["Position"], gray_df["Max"], "red")
    gray_ax.plot(gray_df["Position"], gray_df["Min"], "blue")
    gray_ax.fill_between(gray_df["Position"], y1 = pos_std, y2 = neg_std, color = "gray", alpha = 0.5)
    gray_ax.set_title(f"Axis {quant_axis}")
    gray_ax.tick_params(axis = "both", labelsize = tick_fontsize)
    
    return gray_ax

def gray_level(data: np.ndarray | pd.DataFrame, *,
               return_axes: bool = False,
               mask_array: np.ndarray = None) -> plt.Figure:

    return multi_plot(np.array([data] * 3), (["gray lvl"] * 3), mask_array = mask_array, return_axes = return_axes)

def denoise_ssl_axis(data: np.ndarray | dict, input_axis: plt.Axes, *,
                     denoiser: Callable[[np.ndarray], np.ndarray] = None,
                     parameters: dict[str, np.ndarray] = None,
                     stride: int = 4,
                     approximate_loss: bool = True) -> plt.Axes:
    
    if isinstance(data, np.ndarray):
        
        ssl_dict: dict[str, list] = quant.get_denoising_losses(data, denoiser, parameters,
                                                               stride = stride, approximate_loss = approximate_loss)
        
    else:
        
        ssl_dict: dict[str, list] = data.copy()
    
    if len(ssl_dict["parameters"][0]) == 2:
        
        parameters_tested: list[dict[str, np.float64, np.int64]] = ssl_dict["parameters"]
        losses: list[np.float64] = ssl_dict["losses"]
        labels: list[np.float64 | np.int64] = []
        x_vals: list[np.ndarray] = []
        y_vals: list[np.ndarray] = []
        label_index: int = 0
        
        for index, dict_item in enumerate(parameters_tested):
            
            if index == 0:
                
                prev_label: np.float64 | np.int64 = list(dict_item.values())[0]
                labels.append(prev_label)
                x_vals.append(np.array([list(dict_item.values())[1]]))
                y_vals.append(np.array([losses[index]]))
            
            else:
                
                current_label = list(dict_item.values())[0]
                
                if current_label == prev_label:
                    
                    x_vals[label_index] = np.append(x_vals[label_index], list(dict_item.values())[1])
                    y_vals[label_index] = np.append(y_vals[label_index], losses[index])
                    
                else:
                    
                    label_index += 1
                    labels.append(current_label)
                    x_vals.append(np.array([list(dict_item.values())[1]]))
                    y_vals.append(np.array([losses[index]]))
                    
                prev_label = current_label.copy()
                    
        x_label: str = list(parameters_tested[0].keys())[1].capitalize()
        x_label = x_label.replace("_", " ")
        ssl_ax: plt.Axes = input_axis
        ssl_ax.set_xlabel(x_label, fontsize = label_fontsize)
        ssl_ax.set_ylabel("Mean Squared Error", fontsize = label_fontsize)
        ssl_ax.set_xlim(min(x_vals[0]), max(x_vals[0]))
        color_list: list[np.ndarray] = get_color_list(num_colors = len(labels))
        
        for index, x in enumerate(x_vals):
            
            ssl_ax.plot(x, y_vals[index], color = color_list[index], label = str(labels[index]))
            
        leg_title: str = list(parameters_tested[0].keys())[0].capitalize()
        leg_title = leg_title.replace("_", " ")
        ssl_ax.legend(title = leg_title, fontsize = legend_fontsize)
        
    elif len(ssl_dict["parameters"][0]) == 1:
        
        x_vals: np.ndarray = np.empty(len(ssl_dict["parameters"]))
    
        for index, dict_item in enumerate(ssl_dict["parameters"]):
            
            x_vals[index] = list(dict_item.values())[0]
            
        x_label: str = list(ssl_dict["parameters"][0].keys())[0].capitalize()
        x_label = x_label.replace("_", " ")
        ssl_ax: plt.Axes = input_axis
        ssl_ax.set_xlabel(x_label, fontsize = label_fontsize)
        ssl_ax.set_ylabel("Mean Squared Error", fontsize = label_fontsize)
        ssl_ax.set_xlim(np.min(x_vals), np.max(x_vals))
        ssl_ax.plot(x_vals, ssl_dict["losses"])
        
    ssl_ax.tick_params(axis = "both", labelsize = tick_fontsize)
        
    return ssl_ax

def denoise_ssl(data: np.ndarray | dict, denoiser: Callable[[np.ndarray], np.ndarray] = None,
                parameters: dict[str, np.ndarray] = None, *,
                stride: int = 4,
                approximate_loss: bool = True) -> plt.Figure:
    
    fig, ssl_ax = plt.subplots(layout = "constrained")
    ssl_ax = denoise_ssl_axis(data, ssl_ax, denoiser = denoiser, parameters = parameters,
                              stride = stride, approximate_loss = approximate_loss)
    
    return fig

def heat_axis(
        data: np.ndarray,
        input_ax: plt.Axes, *,
        mode: str = "thick",
        cmap: str = "inferno",
        clim: tuple = None,
        mask_array: np.ndarray = None,
        pixel_size: float = 1.0,
        units: str = "pix", axis: int = 0,
        height_orientation: str = "near",
        return_array: bool = False) -> plt.Axes:
    
    if units == "um":
        
        units = "\u00b5m"
    
    if data.ndim > 2:
        
        heat_array: np.ndarray = distrib.get_heat_map(
            data,
            mode = mode,
            mask_array = mask_array,
            pixel_size = pixel_size,
            axis = axis,
            height_orientation = height_orientation)
    
    else:
        
        heat_array: np.ndarray = np.flipud(np.copy(data))
        
    if not clim:
        
        vmin: float | int = np.min(heat_array)
        vmax: float | int = np.max(heat_array)
        
    else:
        
        vmin: float | int = min(clim)
        vmax: float | int = max(clim)
        
    heat_ax: plt.Axes = input_ax
    ax_im = heat_ax.imshow(
        heat_array, 
        cmap = cmap,
        vmin = vmin,
        vmax = vmax,
        origin = "lower",
        interpolation = "none",
        extent = [
            0,
            (heat_array.shape[1] * pixel_size),
            0,
            (heat_array.shape[0] * pixel_size)])
    heat_ax.set_xlabel(f"Position ({units})", fontsize = label_fontsize)
    heat_ax.set_ylabel(f"Position ({units})", fontsize = label_fontsize)
    heat_ax.tick_params(axis = "both", labelsize = tick_fontsize)
    
    if return_array:
        
        return heat_ax, ax_im, np.flipud(heat_array)
    
    else:
    
        return heat_ax, ax_im

def heat_map(
        data: np.ndarray, *,
        mode: str = "thickness",
        cmap: str = "inferno",
        clim: tuple = None,
        mask_array: np.ndarray = None,
        pixel_size: float = 1.0,
        units: str = "pix",
        axis: int = 0,
        height_orientation: str = "near",
        cbar_label: str = None,
        return_array: bool = False) -> plt.Figure | np.ndarray:
    
    if units == "um":
        
        units = "\u00b5m"
    
    if mode == "thickness" and not cbar_label:
        
        c_label: str = f"Thickness ({units})"
        
    elif mode == "height" and not cbar_label:
        
        c_label: str = f"Height ({units})"
        
    else:
        
        c_label: str = f"{cbar_label} ({units})"
    
    fig, heat_ax = plt.subplots(layout = "constrained")
    heat_ax, ax_im, heat_array = heat_axis(
        data,
        heat_ax,
        mode = mode,
        cmap = cmap,
        clim = clim,
        mask_array = mask_array,
        pixel_size = pixel_size,
        units = units,
        axis = axis,
        height_orientation = height_orientation,
        return_array = True)
    fig_cbar: cbar.Colorbar = fig.colorbar(ax_im)
    fig_cbar.set_label(
        c_label,
        rotation = 270,
        va = "bottom",
        fontsize = label_fontsize)
    fig_cbar.ax.tick_params(labelsize = tick_fontsize)
    
    if np.any(mask_array):
        
        if mask_array.ndim > 2:
            
            heat_mask = mask_array[0]
            
        else:
            
            heat_mask = np.copy(mask_array)
            
    else:
        
        heat_mask = None
        
    if not clim:
        
        vmin: float | int = np.min(heat_array)
        vmax: float | int = np.max(heat_array)
        
    else:
        
        vmin: float | int = min(clim)
        vmax: float | int = max(clim)
        
    heat_stats: dict = quant.global_statistics(
        heat_array,
        mask_array = heat_mask,
        print_results = False).to_dict(orient = "list")
    heat_stats["DType Min"] = [vmin]
    heat_stats["DType Max"] = [vmax]
    heat_hist: pd.DataFrame = distrib.get_histogram(
        heat_array,
        mask_array = heat_mask,
        normalize = True)
    print("\n")
    
    for stat in list(heat_stats.keys()):
        
        current_str: str = stat + ":"
        print(f"{current_str:<16} {heat_stats[stat][0]} {units}")
        
    print(f"{"Max Area Ratio:":<16} {heat_hist.loc[len(heat_hist) - 1]["Counts"]}")
    print(f"{"Min Area Ratio:":<16} {heat_hist.loc[0]["Counts"]}")
    
    if return_array:
        
        return fig, heat_array
    
    else:
    
        return fig

def multi_plot(data_list: list[np.ndarray, pd.DataFrame], function_list: list[str], layout: tuple = None, *,
               return_axes: bool = False,
               x_label: str = "Value",
               mask_array: np.ndarray = None,
               xlims: tuple = None,
               ylims: tuple = None,
               ignore_edges: bool = False,
               normalize: bool = False,
               quant_axes: tuple = (0, 1, 2),
               mode: str = "vol",
               units: str = "pix",
               connectivity: int = None,
               background: float | int = 0) -> plt.Figure:
       
    if len(function_list) == 1:
        
        function_list *= len(data_list)
    
    if not layout:
        
        layout: tuple = subplot_layout(len(data_list))
    
    fig, axs = plt.subplots(layout[0], layout[1])
    
    if any(x == "hist cdf" for x in function_list):
        
        cdf_axs = np.copy(axs)
    
    for index, data in enumerate(data_list):
        
        if function_list[index] == "hist":
            
            axs[index] = histogram_axis(data, axs[index], x_label = x_label, mask_array = mask_array, xlims = xlims, ylims = ylims, ignore_edges = ignore_edges, normalize = normalize)
        
        elif function_list[index] == "cdf":
            
            axs[index] = cdf_axis(data, axs[index], x_label = x_label, mask_array = mask_array, xlims = xlims, ylims = ylims)
        
        elif function_list[index] == "hist cdf":
            
            axs[index] = histogram_axis(data, axs[index], x_label = x_label, mask_array = mask_array, xlims = xlims, ylims = ylims, ignore_edges = ignore_edges, normalize = normalize)
            cdf_axs[index]: plt.Axes = axs[index].twinx()
            cdf_axs[index].set_ylabel("Probability", rotation = 270, va = "bottom", fontsize = label_fontsize)
            cdf_axs[index] = cdf_axis(data, cdf_axs[index], x_label = x_label, mask_array = mask_array, xlims = xlims)
            
        elif function_list[index] == "gray lvl":
            
            axs[index] = gray_level_axis(data, axs[index], quant_axes[index], mask_array = mask_array)
            
        elif function_list[index] == "ssl":
            
            axs[index] = denoise_ssl_axis(data, axs[index])
            
        elif function_list[index] == "size":
            
            axs[index] = size_distribution_ax(data, axs[index], mask_array = mask_array, mode = mode, units = units, xlims = xlims, ylims = ylims, ignore_edges = ignore_edges, normalize = normalize, connectivity = connectivity, background = background)
        
    fig.tight_layout()
    
    if return_axes:
        
        if any(x == "hist cdf" for x in function_list):
            
            return axs, cdf_axs
        
        else:
            
            return axs
    
    else:
        
        return fig
    
    
# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()    