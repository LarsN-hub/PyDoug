"""
Module for generating plots to analyze images
"""

# Imports

import numpy as np
import quant

from matplotlib import pyplot as plt
from typing import Callable


# Functions

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

def set_intensity_axlims(axis: plt.Axes, data_type: np.dtype, y_or_x: str = "x", *, axlims: tuple = None) -> plt.Axes:
    
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

def histogram_axis(data: np.ndarray | dict, input_ax: plt.Axes, *, x_label: str = "Value", mask_array: np.ndarray = None, xlims: tuple = None, ylims: tuple = None, ignore_edges: bool = False) -> plt.Axes:
    
    if isinstance(data, np.ndarray):
    
        hist_dict: dict[str, np.ndarray] = quant.get_histogram(data, mask_array = mask_array)
        
    else:
        
        hist_dict: dict[str, np.ndarray] = data.copy()
        
    if ignore_edges:
        
        hist_dict["bin centers"] = hist_dict["bin centers"][1:-1]
        hist_dict["counts"] = hist_dict["counts"][1:-1]
        
    hist_ax: plt.Axes = input_ax
    hist_ax.set_xlabel(x_label)
    hist_ax.set_ylabel("Counts")
    hist_ax.hist(hist_dict["bin centers"], hist_dict["bin centers"], weights = hist_dict["counts"])
    
    if xlims:
        
        hist_ax = set_intensity_axlims(hist_ax, hist_dict["bin centers"].dtype, "x", axlims = xlims)
        
    else:
        
        hist_ax.set_xlim(np.min(hist_dict["bin centers"]), np.max(hist_dict["bin centers"]))
        
    if ylims:
        
        hist_ax.set_ylim(min(ylims), max(ylims))
        
    return hist_ax

def histogram(data: np.ndarray | dict, *, x_label: str = "Value", mask_array: np.ndarray = None, xlims: tuple = None, ylims: tuple = None, ignore_edges: bool = False) -> plt.Figure:
    
    fig, hist_ax = plt.subplots()
    hist_ax = histogram_axis(data, hist_ax, x_label = x_label, mask_array = mask_array, xlims = xlims, ylims = ylims, ignore_edges = ignore_edges)
    
    return fig

def cdf_axis(data: np.ndarray | dict, input_ax: plt.Axes, *, mask_array: np.ndarray = None, xlims: tuple = None, ylims: tuple = None) -> plt.Axes:
    
    if isinstance(data, np.ndarray):
    
        cdf_dict: dict[str, np.ndarray] = quant.get_cdf(data, mask_array = mask_array)
        
    else:
        
        cdf_dict: dict[str, np.ndarray] = data.copy()
        
    cdf_ax: plt.Axes = input_ax
    cdf_ax.set_xlabel("Gray Value")
    cdf_ax.set_ylabel("Probability")
    cdf_ax.set_ylim(0, 1)
    cdf_ax.plot(cdf_dict["bin centers"], cdf_dict["cdf"], "red")
    
    if xlims:
        
        cdf_ax = set_intensity_axlims(cdf_ax, cdf_dict["bin centers"].dtype, "x", axlims = xlims)
        
    else:
        
        cdf_ax.set_xlim(np.min(cdf_dict["bin centers"]), np.max(cdf_dict["bin centers"]))
        
    if ylims:
        
        cdf_ax.set_ylim(min(ylims), max(ylims))
        
    return cdf_ax

def cdf(data: np.ndarray | dict, *, mask_array: np.ndarray = None, xlims: tuple = None, ylims: tuple = None) -> plt.Figure:
    
    fig, cdf_ax = plt.subplots()
    cdf_ax = cdf_axis(data, cdf_ax, mask_array = mask_array, xlims = xlims, ylims = ylims)
    
    return fig

def hist_cdf(data: np.ndarray | dict, *, x_label: str = "Value", mask_array: np.ndarray = None, xlims: tuple = None, ylims: tuple = None, ignore_edges: bool = False) -> plt.Figure:
    
    fig, hist_ax = plt.subplots()
    hist_ax = histogram_axis(data, hist_ax, x_label = x_label, mask_array = mask_array, xlims = xlims, ylims = ylims, ignore_edges = ignore_edges)
    cdf_ax: plt.Axes = hist_ax.twinx()
    cdf_ax = cdf_axis(data, cdf_ax, mask_array = mask_array, xlims = xlims, ylims = ylims)
    cdf_ax.set_ylabel("Probability", rotation = 270, va = "bottom")
    
    return fig

def denoise_ssl_axis(data: np.ndarray | dict, input_axis: plt.Axes, *, denoiser: Callable[[np.ndarray], np.ndarray] = None,
                     parameters: dict[str, np.ndarray] = None, stride: int = 4, approximate_loss: bool = True) -> plt.Axes:
    
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
                    
        color_base: np.ndarray = np.array([0.121, 0.465, 0.703])
        color_final: np.ndarray = np.array([0.703, 0.047, 0.047])
        color_inc: np.ndarray = (color_final - color_base) / (len(labels) - 1)
        color_list: list[tuple] = []
        
        for index in range(0, len(labels)):
            
            if index == 0:
                
                color_list.append(tuple(color_base))
                
            else:
                
                color_list.append(tuple(color_base + (index * color_inc)))
                    
        x_label: str = list(parameters_tested[0].keys())[1].capitalize()
        x_label = x_label.replace("_", " ")
        ssl_ax: plt.Axes = input_axis
        ssl_ax.set_xlabel(x_label)
        ssl_ax.set_ylabel("Mean Squared Error")
        ssl_ax.set_xlim(min(x_vals[0]), max(x_vals[0]))
        
        for index, x in enumerate(x_vals):
            
            ssl_ax.plot(x, y_vals[index], color = color_list[index], label = str(labels[index]))
            
        leg_title: str = list(parameters_tested[0].keys())[0].capitalize()
        leg_title = leg_title.replace("_", " ")
        ssl_ax.legend(title = leg_title)
        
    elif len(ssl_dict["parameters"][0]) == 1:
        
        x_vals: np.ndarray = np.empty(len(ssl_dict["parameters"]))
    
        for index, dict_item in enumerate(ssl_dict["parameters"]):
            
            x_vals[index] = list(dict_item.values())[0]
            
        x_label: str = list(ssl_dict["parameters"][0].keys())[0].capitalize()
        x_label = x_label.replace("_", " ")
        ssl_ax: plt.Axes = input_axis
        ssl_ax.set_xlabel(x_label)
        ssl_ax.set_ylabel("Mean Squared Error")
        ssl_ax.set_xlim(np.min(x_vals), np.max(x_vals))
        ssl_ax.plot(x_vals, ssl_dict["losses"])
        
    return ssl_ax

def denoise_ssl(data: np.ndarray | dict, denoiser: Callable[[np.ndarray], np.ndarray] = None,
                parameters: dict[str, np.ndarray] = None, *, stride: int = 4, approximate_loss: bool = True) -> plt.Figure:
    
    fig, ssl_ax = plt.subplots()
    ssl_ax = denoise_ssl_axis(data, ssl_ax, denoiser = denoiser, parameters = parameters,
                              stride = stride, approximate_loss = approximate_loss)
    
    return fig

def gray_level_axis(data: np.ndarray | dict, input_ax: plt.Axes, quant_axis: int = 0, *, mask_array: np.ndarray = None) -> plt.Axes:
    
    if isinstance(data, np.ndarray):
        
        gray_dict: dict[int, np.ndarray] = quant.single_ax_statistics(data, quant_axis, mask_array = mask_array)
    
    else:
        
        gray_dict: dict[int, np.ndarray] = data.copy()
        
    pos_std: np.ndarray = gray_dict["mean"] + gray_dict["stdev"]
    neg_std: np.ndarray = gray_dict["mean"] - gray_dict["stdev"]
    gray_ax: plt.Axes = input_ax
    gray_ax.set_xlabel("Position [pixels]")
    gray_ax.set_ylabel("Gray Value")
    gray_ax.set_xlim(0, np.max(gray_dict["position"]))
    gray_ax.plot(gray_dict["position"], gray_dict["mean"], "black")
    gray_ax.plot(gray_dict["position"], gray_dict["max"], "red")
    gray_ax.plot(gray_dict["position"], gray_dict["min"], "blue")
    gray_ax.fill_between(gray_dict["position"], y1 = pos_std, y2 = neg_std, color = "gray", alpha = 0.5)
    gray_ax.set_title(f"Axis {quant_axis}")
    
    return gray_ax

def gray_level(data: np.ndarray | dict, *, mask_array: np.ndarray = None) -> plt.Figure:

    return multi_plot(np.array([data] * 3), (["gray lvl"] * 3), mask_array = mask_array)

def multi_plot(data_array: np.ndarray, function_list: list[str], layout: tuple = None, *, x_label: str = "Value", mask_array: np.ndarray = None, xlims: tuple = None, ylims: tuple = None, ignore_edges: bool = False, quant_axes: tuple = (0, 1, 2)) -> plt.Figure:
       
    if len(function_list) == 1:
        
        function_list *= data_array.shape[0]
    
    if not layout:
        
        layout: tuple = subplot_layout(len(data_array))
    
    fig, axs = plt.subplots(layout[0], layout[1])
    
    if any(x == "hist cdf" for x in function_list):
        
        cdf_axs = np.copy(axs)
    
    for index, data in enumerate(data_array):
        
        if function_list[index] == "hist":
            
            axs[index] = histogram_axis(data, axs[index], x_label = x_label, mask_array = mask_array, xlims = xlims, ylims = ylims, ignore_edges = ignore_edges)
        
        elif function_list[index] == "cdf":
            
            axs[index] = cdf_axis(data, axs[index], mask_array = mask_array, xlims = xlims, ylims = ylims)
        
        elif function_list[index] == "hist cdf":
            
            axs[index] = histogram_axis(data, axs[index], x_label = x_label, mask_array = mask_array, xlims = xlims, ylims = ylims, ignore_edges = ignore_edges)
            cdf_axs[index]: plt.Axes = axs[index].twinx()
            cdf_axs[index] = cdf_axis(data, cdf_axs[index], mask_array = mask_array, xlims = xlims)
            cdf_axs[index].set_ylabel("Probability", rotation = 270, va = "bottom")
            
        elif function_list[index] == "gray lvl":
            
            axs[index] = gray_level_axis(data, axs[index], quant_axes[index], mask_array = mask_array)
            
        elif function_list[index] == "ssl":
            
            axs[index] = denoise_ssl_axis(data, axs[index])
        
    fig.tight_layout()
    
    return fig
        
    
# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()    