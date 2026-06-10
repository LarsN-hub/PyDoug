"""
Module for generating plots to analyze images
"""


# Imports

import pandas as pd, numpy as np, napari, math

from matplotlib import colorbar as cbar, pyplot as plt, transforms as tr, ticker
from typing import Callable

from PyDoug.analyze import distrib, quant
from PyDoug.ui import sliceview as sv
from PyDoug.proc import util, cropclip as cc


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

def get_color_list(
        mode: str = "br",
        num_colors: int = 2) -> list[np.ndarray]:
    
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

def generate_log_ticks(ax: plt.Axes, ax_lims: tuple):
    
    oom_1: int = util.find_order_of_mag(ax_lims[0])
    oom_2: int = util.find_order_of_mag(ax_lims[1])
    if oom_2 - oom_1 < 2:
        alt_start: int = math.floor(ax_lims[0] / (10 ** oom_1))
        alt_end: int = math.ceil(ax_lims[1] / (10 ** oom_1)) + 1
        if alt_start % 2 != 0:
            alt_start -= 1
        ticks: np.ndarray = np.arange(alt_start, alt_end, 2)
        if ticks[0] == 0:
            ticks = ticks[1:]
        if ticks[0] == 2:
            ticks = np.concat((np.array([1]), ticks))
        ticks = ticks * (10 ** oom_1)
        return ticks
    else:
        return ax.get_xticks()

def remove_edges(
        data_df: pd.DataFrame) -> pd.DataFrame:
    
    data_df = data_df[1:-1].reset_index(drop = True)
    eval_array: np.ndarray = np.array(data_df[data_df.columns[1:]]) != 0
    new_start: int = 0
    new_end: int = 0
    
    for col_index in range(0, eval_array.shape[1]):
        cur_start_array: np.ndarray = np.nonzero(eval_array[:, col_index])[0]
        if not cur_start_array.shape[0]:
            continue
        else:
            cur_start: int = cur_start_array[0]
            cur_end: int = np.nonzero(eval_array[:, col_index])[0][-1]
        if col_index == 0:
            new_start = cur_start
            new_end = cur_end
        if cur_start < new_start:
            new_start = cur_start
        if cur_end > new_end:
            new_end = cur_end
    
    return data_df[new_start: new_end].reset_index(drop = True)

def subplot_layout(
        num_plots: int) -> tuple:
    
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

def set_axlims(
        axis: plt.Axes,
        data_type: np.dtype,
        y_or_x: str = "x", *,
        axlims: tuple = None) -> plt.Axes:
    
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

def get_log_starts_widths(
        log_ax_values: np.ndarray, *,
        points_per_value: int = 1,
        point_count_index: int = 0,
        width: float = 1) -> np.ndarray:
    
    offset_starts: np.ndarray = np.zeros((points_per_value, log_ax_values.shape[0]))
    widths: np.ndarray = np.copy(offset_starts)
    offset_indices: np.ndarray = np.arange(0, points_per_value)
    offset_indices = offset_indices - math.floor((points_per_value / 2))
    
    for index, value in enumerate(log_ax_values):
        log_left: np.ndarray = np.logspace(
            math.log10(value) - 1,
            math.log10(value),
            max(round(10 / width), points_per_value))
        log_right: np.ndarray = np.logspace(
            math.log10(value),
            math.log10(value) + 1,
            max(round(10 / width), points_per_value))
        log_range: np.ndarray = np.concat((log_left, log_right[1:]))
        for point_index in range(point_count_index, points_per_value):
            offset_starts[point_index, index] = log_range[
                (max(round(10 / width), points_per_value) - 1) + offset_indices[point_index]]
            widths[point_index, index] = log_range[
                (max(round(10 / width), points_per_value) - 1) + offset_indices[point_index] + 1] - log_range[(max(round(10 / width), points_per_value) - 1) + offset_indices[point_index]]
    
    return offset_starts, widths

def line_axis(
        data: np.ndarray | pd.DataFrame = None,
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
            line_df: pd.DataFrame = sv.quick_get_line_scan(
                viewer,
                slice_range,
                pixel_size = pixel_size,
                units = units)
        
        elif mode == "phase distrib":
            line_df: pd.DataFrame = distrib.get_position_distribution(
                data,
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
            line_df: pd.DataFrame = distrib.get_size_distribution(
                data,
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
            line_df: pd.DataFrame = distrib.get_time_series(
                data,
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
    color_list: list[np.ndarray] = get_color_list(
        color_mode,
        len(line_df.columns) - 1)
    
    for index, column in enumerate(line_df.columns):
        if index == 0:
            x_values: pd.Series = line_df[column]
        else:
            line_ax.plot(
                x_values,
                line_df[column],
                color = color_list[index - 1],
                linewidth = 2)
    
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

def line(
        data: np.ndarray | pd.DataFrame,
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
    line_ax, line_df = line_axis(
        data,
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

def gui_line_scan(
        im_array: np.ndarray,
        shapes_layer: napari.layers.Shapes) -> plt.Figure:
    
    line_scan_df: pd.DataFrame = sv.quick_get_line_scan(
        im_array = im_array,
        shapes_layer = shapes_layer)
    fig, ls_ax = plt.subplots(layout = "constrained")
    ls_ax.set_xlabel("Position [pix]", fontsize = label_fontsize)
    ls_ax.set_ylabel("Gray Value", fontsize = label_fontsize)
    ls_ax.plot(line_scan_df["Position"], line_scan_df["Gray Value"], "red", linewidth = 2)
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
        
    if np.sum(hist_df["Counts"]) != 0:
        hist_mean: float = np.sum(
            (np.array(hist_df["Bin Centers"]) * np.array(hist_df["Counts"]))) / np.sum(hist_df["Counts"])
        print(f"\n{"Histogram Mean:":<16} {hist_mean}")
        
        if not normalize:
            ext_bin_centers: np.ndarray = distrib.extend_histogram_bins(
                np.array(hist_df["Bin Centers"]),
                np.array(hist_df["Counts"]))
            hist_med: float = np.median(ext_bin_centers)
            hist_std: float = quant.get_std(ext_bin_centers)
            print(f"{"Histogram Med:":<16} {hist_med}")
            print(f"{"Histogram StDv:":<16} {hist_std}")
            print(f"{"Total Counts:":<16} {ext_bin_centers.size}")
            hist_stats_df: pd.DataFrame = pd.DataFrame(
                np.array([
                    [hist_mean,
                     hist_med,
                     hist_std,
                     ext_bin_centers.size]]),
                columns = ["Mean", "Median", "Std. Dev.", "Counts"])
        else:
            hist_stats_df: pd.DataFrame = pd.DataFrame(
                np.array([[hist_mean]]),
                columns = ["Mean"])
            
    else:
        hist_stats_df: pd.DataFrame = pd.DataFrame(
            np.array([[0, 0, 0, 0]]),
            columns = ["Mean", "Median", "Std. Dev.", "Counts"])
        
    if ignore_edges:
        hist_df = remove_edges(hist_df)
        
    hist_ax: plt.Axes = input_ax
    hist_ax.set_xlabel(x_label, fontsize = label_fontsize)
    
    if normalize:
        hist_ax.set_ylabel("Probability Density", fontsize = label_fontsize)
    else:
        hist_ax.set_ylabel("Counts", fontsize = label_fontsize)
        
    hist_ax.hist(
        hist_df["Bin Centers"],
        hist_df["Bin Centers"],
        weights = hist_df["Counts"],
        edgecolor = "k")
    
    if xlims:
        hist_ax = set_axlims(
            hist_ax,
            hist_df["Bin Centers"].dtype,
            "x",
            axlims = xlims)
    else:
        hist_ax.set_xlim(
            np.min(hist_df["Bin Centers"]),
            np.max(hist_df["Bin Centers"]))
        
    if ylims:
        hist_ax.set_ylim(min(ylims), max(ylims))
    if logx:
        hist_ax.set_xscale("log")
        
    hist_ax.tick_params(
        axis = "both",
        labelsize = tick_fontsize)
        
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
        calc_sphericity: bool = False,
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
            max_bound = max_bound,
            calc_sphericity = calc_sphericity)
    
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
        calc_sphericity: bool = False,
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
        calc_sphericity = calc_sphericity,
        return_df = True)
    
    if return_df:
        return fig, psd_df, hist_stats_df
    else:
        return fig

def cdf_axis(
        data: np.ndarray | pd.DataFrame,
        input_ax: plt.Axes, *,
        x_label: str = "Value",
        mask_array: np.ndarray = None,
        xlims: tuple = None,
        ylims: tuple = None) -> plt.Axes:
    
    if isinstance(data, np.ndarray):
        cdf_df: pd.DataFrame = distrib.get_cdf(
            data,
            mask_array = mask_array)
    else:
        cdf_df: pd.DataFrame = data.copy()
        
    cdf_ax: plt.Axes = input_ax
    cdf_ax.set_xlabel(x_label, fontsize = label_fontsize)
    cdf_ax.set_ylabel("Probability", fontsize = label_fontsize)
    cdf_ax.set_ylim(0, 1)
    cdf_ax.plot(cdf_df["Bin Centers"], cdf_df["Probability"], "red", linewidth = 2)
    
    if xlims:
        cdf_ax = set_axlims(
            cdf_ax,
            cdf_df["Bin Centers"].dtype,
            "x",
            axlims = xlims)
    else:
        cdf_ax.set_xlim(
            np.min(
                cdf_df["Bin Centers"]),
            np.max(cdf_df["Bin Centers"]))
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
    cdf_ax = cdf_axis(
        data,
        cdf_ax,
        mask_array = mask_array,
        xlims = xlims,
        ylims = ylims)
    
    return fig

def hist_cdf(
        data: np.ndarray | dict, *,
        x_label: str = "Value",
        mask_array: np.ndarray = None,
        xlims: tuple = None,
        ylims: tuple = None,
        ignore_edges: bool = False,
        normalize: bool = False) -> plt.Figure:
    
    fig, hist_ax = plt.subplots(layout = "constrained")
    hist_ax = histogram_axis(
        data,
        hist_ax,
        x_label = x_label,
        mask_array = mask_array,
        xlims = xlims,
        ylims = ylims,
        ignore_edges = ignore_edges,
        normalize = normalize)
    cdf_ax: plt.Axes = hist_ax.twinx()
    cdf_ax.set_ylabel(
        "Probability",
        rotation = 270,
        va = "bottom",
        fontsize = label_fontsize)
    cdf_ax = cdf_axis(
        data,
        cdf_ax,
        x_label = x_label,
        mask_array = mask_array,
        xlims = xlims,
        ylims = ylims)
    
    return fig

def gray_level_axis(
        data: np.ndarray | pd.DataFrame,
        input_ax: plt.Axes,
        quant_axis: int = 0, *,
        mask_array: np.ndarray = None) -> plt.Axes:
    
    if isinstance(data, np.ndarray):
        gray_df: pd.DataFrame = quant.single_ax_statistics(
            data,
            quant_axis,
            mask_array = mask_array)
    else:
        gray_df: pd.DataFrame = data.copy()
        
    pos_std: np.ndarray = gray_df["Mean"] + gray_df["Std Dev"]
    neg_std: np.ndarray = gray_df["Mean"] - gray_df["Std Dev"]
    gray_ax: plt.Axes = input_ax
    gray_ax.set_xlabel("Position [pixels]", fontsize = label_fontsize)
    gray_ax.set_ylabel("Gray Value", fontsize = label_fontsize)
    gray_ax.set_xlim(0, max(gray_df["Position"]))
    gray_ax.plot(gray_df["Position"], gray_df["Mean"], "black", linewidth = 2)
    gray_ax.plot(gray_df["Position"], gray_df["Max"], "red", linewidth = 2)
    gray_ax.plot(gray_df["Position"], gray_df["Min"], "blue", linewidth = 2)
    gray_ax.fill_between(
        gray_df["Position"],
        y1 = pos_std,
        y2 = neg_std,
        color = "gray",
        alpha = 0.5)
    gray_ax.set_title(f"Axis {quant_axis}")
    gray_ax.tick_params(axis = "both", labelsize = tick_fontsize)
    
    return gray_ax

def gray_level(
        data: np.ndarray | pd.DataFrame, *,
        return_axes: bool = False,
        mask_array: np.ndarray = None) -> plt.Figure:

    return multi_plot(
        np.array([data] * 3),
        (["gray lvl"] * 3),
        mask_array = mask_array,
        return_axes = return_axes)

def denoise_ssl_axis(
        data: np.ndarray | dict,
        input_axis: plt.Axes, *,
        denoiser: Callable[[np.ndarray], np.ndarray] = None,
        parameters: dict[str, np.ndarray] = None,
        stride: int = 4,
        approximate_loss: bool = True) -> plt.Axes:
    
    if isinstance(data, np.ndarray):
        ssl_dict: dict[str, list] = quant.get_denoising_losses(
            data,
            denoiser,
            parameters,
            stride = stride,
            approximate_loss = approximate_loss)
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
                    x_vals[label_index] = np.append(
                        x_vals[label_index], list(dict_item.values())[1])
                    y_vals[label_index] = np.append(
                        y_vals[label_index], losses[index])
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

def denoise_ssl(
        data: np.ndarray | dict,
        denoiser: Callable[[np.ndarray], np.ndarray] = None,
        parameters: dict[str, np.ndarray] = None, *,
        stride: int = 4,
        approximate_loss: bool = True) -> plt.Figure:
    
    fig, ssl_ax = plt.subplots(layout = "constrained")
    ssl_ax = denoise_ssl_axis(
        data,
        ssl_ax,
        denoiser = denoiser,
        parameters = parameters,
        stride = stride,
        approximate_loss = approximate_loss)
    
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
    heat_ax.xaxis.set_major_locator(ticker.AutoLocator())
    #heat_ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
    #heat_ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
    
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
    
def resolution_dependence_axis(
        data: np.ndarray | pd.DataFrame,
        input_ax: plt.Axes, *,
        metric: str = "bulk",
        bulk_method: str = "phase",
        estimate_fractal: bool = False,
        pixel_size: float = 1,
        units: str = "pix",
        bounds: tuple = None,
        num_points: int = 10,
        logspace_points: bool = True,
        correct_overestimation: bool = True,
        xlims: tuple = None,
        ylims: tuple = None,
        mask_array: np.ndarray = None) -> plt.Axes | pd.DataFrame:
    
    if isinstance(data, np.ndarray):
        data_df: pd.DataFrame = distrib.get_resolution_dependence(
            data,
            metric = metric,
            bulk_method = bulk_method,
            estimate_fractal = estimate_fractal,
            pixel_size = pixel_size,
            units = units,
            bounds = bounds,
            num_points = num_points,
            logspace_points = logspace_points,
            correct_overestimation = correct_overestimation,
            mask_array = mask_array)
        if util.is_3d_rgb(data)["3D"]:
            x_title: str = "Voxel Size"
            if metric == "bulk":
                y_label: str = f"Volume ({units}\u00b3)"
            elif metric == "surface":
                y_label: str = f"Surface Area ({units}\u00b2)"
            elif metric == "specific surface":
                y_label: str = f"Specific Surface Area (1/{units})"
        else:
            x_title: str = "Pixel Size"
            if metric == "bulk":
                y_label: str = f"Area ({units}\u00b2)"
            elif metric == "surface":
                y_label: str = f"Surface Perimeter ({units})"
            elif metric == "specific surface":
                y_label: str = f"Specific Perimeter (1/{units})"
    else:
        data_df: pd.DataFrame = data.copy()
        x_title: str = "Pixel Size"
        y_label: str = "Measured Quantity"
        
    x_units: str = data_df.attrs["units"]
    x_label: str = f"{x_title} ({x_units})"
    if estimate_fractal:
        y_label: str = "Fractal Dimension"
    res_dep_ax: plt.Axes = input_ax
    if estimate_fractal:
        res_dep_ax.plot(
            data_df["Pixel Size"],
            data_df["Measured Value"],
            color = np.array([0.121, 0.465, 0.703]),
            linewidth = 2)
    else:
        res_dep_ax.scatter(
            data_df["Pixel Size"],
            data_df["Measured Value"],
            facecolors = "w",
            edgecolor = np.array([0.121, 0.465, 0.703]),
            linewidth = 1.5,
            s = 75)
    res_dep_ax.set_xlabel(x_label, fontsize = label_fontsize)
    res_dep_ax.set_ylabel(y_label, fontsize = label_fontsize)
    res_dep_ax.tick_params(axis = "both", labelsize = tick_fontsize)
    res_dep_ax.set_xscale("log")
    res_dep_ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    res_dep_ax.set_xlim(xlims)
    if not xlims:
        xlims: tuple = res_dep_ax.get_xlim()
    #res_dep_ax.set_xticks(generate_log_ticks(res_dep_ax, xlims))
    res_dep_ax.set_ylim(ylims)
    return res_dep_ax, data_df

def resolution_dependence_plot(
        data: np.ndarray | pd.DataFrame, *,
        metric: str = "bulk",
        bulk_method: str = "phase",
        estimate_fractal: bool = False,
        pixel_size: float = 1,
        units: str = "pix",
        bounds: tuple = None,
        num_points: int = 10,
        logspace_points: bool = True,
        correct_overestimation: bool = True,
        xlims: tuple = None,
        ylims: tuple = None,
        mask_array: np.ndarray = None,
        return_df: bool = False) -> plt.Figure:
    
    if np.any(mask_array) and isinstance(data, np.ndarray):
        if mask_array.ndim < data.ndim:
            mask_array = cc.project_mask(np.bool(mask_array), data.shape[0])
    
    fig, res_dep_ax = plt.subplots(layout = "constrained")
    res_dep_ax, res_dep_df = resolution_dependence_axis(
        data,
        res_dep_ax,
        metric = metric,
        bulk_method = bulk_method,
        estimate_fractal = estimate_fractal,
        pixel_size = pixel_size,
        units = units,
        bounds = bounds,
        num_points = num_points,
        logspace_points = logspace_points,
        correct_overestimation = correct_overestimation,
        xlims = xlims,
        ylims = ylims,
        mask_array = np.copy(mask_array))
    if return_df:
        return fig, res_dep_df
    else:
        return fig

def multi_plot(
        data_list: list[np.ndarray, pd.DataFrame],
        function_list: list[str],
        layout: tuple = None, *,
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
            axs[index] = histogram_axis(
                data,
                axs[index],
                x_label = x_label,
                mask_array = mask_array,
                xlims = xlims,
                ylims = ylims,
                ignore_edges = ignore_edges,
                normalize = normalize)
        elif function_list[index] == "cdf":
            axs[index] = cdf_axis(
                data,
                axs[index],
                x_label = x_label,
                mask_array = mask_array,
                xlims = xlims,
                ylims = ylims)
        elif function_list[index] == "hist cdf":
            axs[index] = histogram_axis(
                data,
                axs[index],
                x_label = x_label,
                mask_array = mask_array,
                xlims = xlims,
                ylims = ylims,
                ignore_edges = ignore_edges,
                normalize = normalize)
            cdf_axs[index]: plt.Axes = axs[index].twinx()
            cdf_axs[index].set_ylabel(
                "Probability",
                rotation = 270,
                va = "bottom",
                fontsize = label_fontsize)
            cdf_axs[index] = cdf_axis(
                data,
                cdf_axs[index],
                x_label = x_label,
                mask_array = mask_array,
                xlims = xlims)
        elif function_list[index] == "gray lvl":
            axs[index] = gray_level_axis(
                data,
                axs[index],
                quant_axes[index],
                mask_array = mask_array)
        elif function_list[index] == "ssl":
            axs[index] = denoise_ssl_axis(data, axs[index])
        elif function_list[index] == "size":
            axs[index] = size_distribution_ax(
                data,
                axs[index],
                mask_array = mask_array,
                mode = mode,
                units = units,
                xlims = xlims,
                ylims = ylims,
                ignore_edges = ignore_edges,
                normalize = normalize,
                connectivity = connectivity,
                background = background)
        
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
