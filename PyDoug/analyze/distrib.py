"""
Module for multi-value measurements of images
"""


# Imports

import pandas as pd, numpy as np, math

from skimage import exposure
from porespy import metrics

from PyDoug.analyze import quant
from PyDoug.proc import thresh, pixels, trans, cropclip as cc


# Functions

def get_histogram(
        im_array: np.ndarray, *,
        mask_array: np.ndarray = None,
        normalize: bool = False,
        nbins: int = 256,
        max_bound: float | None = None) -> pd.DataFrame:
    
    if max_bound:
        
        im_array[im_array > max_bound] = max_bound
    
    if np.any(mask_array):
        
        if mask_array.ndim < im_array.ndim:
            
            mask_array = cc.project_mask(mask_array, im_array.shape[0])
    
        counts, bin_centers = exposure.histogram(
            im_array[np.bool(mask_array)],
            normalize = normalize,
            nbins = nbins)
        
    else:
        
        counts, bin_centers = exposure.histogram(
            im_array,
            normalize = normalize,
            nbins = nbins)
        
    bin_centers = np.astype(bin_centers, im_array.dtype)
    
    return pd.DataFrame(
        np.stack((bin_centers, counts), 1),
        columns = ["Bin Centers", "Counts"])

def extend_histogram_bins(
        bins: np.ndarray,
        counts: np.ndarray) -> np.ndarray:
    
    ext_bins: np.ndarray = np.empty((1, np.astype(np.sum(counts), np.int32)))
    index: int = 0
    bin_loc: int = 0
    
    for bin_value in bins:
        
        for count in range(0, int(counts[bin_loc])):
            
            ext_bins[0, index] = bin_value
            index += 1
            
        bin_loc += 1
        
    return np.squeeze(ext_bins)

def get_cdf(
        im_array: np.ndarray, *,
        mask_array: np.ndarray = None) -> pd.DataFrame:
    
    if np.any(mask_array):
        
        if mask_array.ndim < im_array.ndim:
            
            mask_array = cc.project_mask(mask_array, im_array.shape[0])
    
        im_cdf, bin_centers = exposure.cumulative_distribution(
            im_array[np.bool(mask_array)])
        
    else:
        
        im_cdf, bin_centers = exposure.cumulative_distribution(
            im_array)
        
    bin_centers = np.astype(bin_centers, im_array.dtype)
        
    return pd.DataFrame(
        np.stack((bin_centers, im_cdf), 1),
        columns = ["Bin Centers", "Probability"])

def get_position_distribution(
        im_array: np.ndarray, *,
        mask_array: np.ndarray = None,
        mode: str = "vol",
        pixel_size: float = 1.0,
        units: str = "pix",
        temporal_scale: float | int = None,
        temporal_units: str = "s",
        axis: int = 0,
        include_background: bool = False,
        background: float | int = 0,
        normalize: bool = False,
        norm_method: str = "total") -> pd.DataFrame:
    
    if units == "um":
        
        units = "\u00b5m"
    
    if temporal_scale:
        
        pos_scale = temporal_scale
        pos_units = temporal_units
        
    else:
        
        pos_scale = pixel_size
        pos_units = units
    
    phases: np.ndarray = np.unique(im_array)
    
    if not include_background:
        
        phases = np.delete(phases, np.argwhere(phases == background))
        
    pos_array: np.ndarray = np.zeros((im_array.shape[axis], 1 + len(phases)))
    
    if np.any(mask_array):
        
        if mask_array.ndim < im_array.ndim:
            
            mask_array = cc.project_mask(mask_array, im_array.shape[0])
    
    for slice_index in range(0, im_array.shape[axis]):
        
        pos_array[slice_index, 0] = slice_index * pos_scale
    
        if axis == 0:
            
            int_im_array: np.ndarray = im_array[slice_index]
            
            if np.any(mask_array):
                
                int_mask_array: np.ndarray = mask_array[slice_index]
                
            else:
                
                int_mask_array = None
            
        elif axis == 1:
            
            int_im_array: np.ndarray = im_array[:, slice_index, :]
            
            if np.any(mask_array):
                
                int_mask_array: np.ndarray = mask_array[:, slice_index, :]
                
            else:
                
                int_mask_array = None
        
        elif axis == 2:

            int_im_array: np.ndarray = im_array[:, :, slice_index]
            
            if np.any(mask_array):
                
                int_mask_array: np.ndarray = mask_array[:, :, slice_index]
                
            else:
                
                int_mask_array = None
                
        if normalize and norm_method == "total":
            
            quant_normalize: bool = True
            
        else:
            
            quant_normalize: bool = False
            
        int_array: np.ndarray = quant.__vol_area_precondition(
            int_im_array,
            mask_array = int_mask_array,
            include_background = include_background,
            background = background,
            normalize = quant_normalize).T
        
        for index, gray_value in enumerate(int_array[:, 0]):
            
            pos_array[slice_index, 1 + np.argwhere(phases == gray_value)] = int_array[index, 1]
            
    if normalize and norm_method == "phase":
        
        for index in range(1, pos_array.shape[1]):
            
            pos_array[:, index] = pos_array[:, index] / np.sum(pos_array[:, index])
            
    if temporal_scale:
        
        columns = ["Time"]
        
    else:
        
        columns = ["Position"]
    
    for phase in phases:
        
        columns.append(str(phase))
            
    if mode == "vol":
        
        if not normalize:
            
            pos_array[:, 1:] = pos_array[:, 1:] * (pixel_size ** 3)
            
        pos_df: pd.DataFrame = pd.DataFrame(pos_array, columns = columns)
        
        if temporal_scale:
            
            pos_df.attrs = {"time_units": f"{pos_units}"}
            
        else:
            
            pos_df.attrs = {"pos_units": f"{pos_units}"}
            
        if not normalize:
            
            pos_df.attrs["vol_units"] = f"{units}\u00b3"
            
        else:
            
            pos_df.attrs["vol_units"] = "dimensionless"
        
    elif mode == "area":
        
        if not normalize:
            
            pos_array[:, 1:] = pos_array[:, 1:] * (pixel_size ** 2)
            
        pos_df: pd.DataFrame = pd.DataFrame(pos_array, columns = columns)
        
        if temporal_scale:
            
            pos_df.attrs = {"time_units": f"{pos_units}"}
            
        else:
            
            pos_df.attrs = {"pos_units": f"{pos_units}"}
            
        if not normalize:
            
            pos_df.attrs["area_units"] = f"{units}\u00b2"
            
        else:
            
            pos_df.attrs["area_units"] = "dimensionless"
        
    return pos_df

def __get_size_distribution(
        im_array: np.ndarray, *,
        mask_array: np.ndarray = None,
        mode: str = "vol",
        diam_rad_mode: str = "vol",
        pixel_size: float = 1.0,
        units: str = "pix",
        background: float | int = 0,
        normalize: bool = False,
        nbins: int | None = None,
        max_bound: float | None = None) -> pd.DataFrame:
    
    if units == "um":
        
        units = "\u00b5m"
    
    if np.any(mask_array):
        
        if mask_array.ndim < im_array.ndim:
            
            mask_array = cc.project_mask(mask_array, im_array.shape[0])
        
        counts, labels = exposure.histogram(im_array[np.bool(mask_array)])
        counts = np.delete(counts, np.argwhere(counts == 0))
        
    else:
        
        counts, labels = exposure.histogram(im_array)
        
    counts = np.astype(
        np.delete(counts, np.argwhere(labels == background)),
        np.float64)
    
    if mode == "vol":
            
        counts = counts * (pixel_size ** 3)
            
    elif mode == "area":
            
        counts = counts * (pixel_size ** 2)
            
    elif mode == "diam":
        
        if diam_rad_mode == "vol":
            
            counts = np.cbrt((counts * (pixel_size ** 3)) / ((4 / 3) * np.pi)) * 2
        
        elif diam_rad_mode == "area":
            
            counts = np.sqrt((counts * (pixel_size ** 2)) / np.pi) * 2
            
    elif mode == "rad":
        
        if diam_rad_mode == "vol":
            
            counts = np.cbrt((counts * (pixel_size ** 3)) / ((4 / 3) * np.pi))
        
        elif diam_rad_mode == "area":
        
            counts = np.sqrt((counts * (pixel_size ** 2)) / np.pi)
    
    if len(counts) != 0:
        
        if nbins:
            
            if max_bound:
                
                counts[counts > max_bound] = max_bound
            
            size_counts, sizes = exposure.histogram(counts, nbins = nbins)
            
            if max_bound:
                
                size_counts[-1] = 0
           
        else:
            
            size_counts, sizes = exposure.histogram(counts)
        
    else:
        
        size_counts: np.ndarray = np.array([0, 0])
        sizes: np.ndarray = np.array([1, 2])
        
    size_counts = np.astype(size_counts, np.int64)
    
    if normalize:
        
        size_counts = size_counts / np.sum(size_counts)
    
    size_df: pd.DataFrame = pd.DataFrame(
        np.stack((sizes, size_counts), 1),
        columns = ["Bin Centers", "Counts"])
    
    if mode == "vol":
        
        size_df.attrs = {"units": f"{units}\u00b3"}
        
    elif mode == "area":
        
        size_df.attrs = {"units": f"{units}\u00b2"}
        
    elif mode == "diam" or mode == "rad":
        
        size_df.attrs = {"units": units}
        
    return size_df

def get_size_distribution(
        im_array: np.ndarray, *,
        mask_array: np.ndarray = None,
        mode: str = "vol",
        diam_rad_mode: str = "vol",
        pixel_size: float = 1.0,
        units: str = "pix",
        connectivity: int = None,
        background: float | int = 0,
        normalize: bool = False,
        nbins: int | None = None,
        max_bound: float | None = None,
        positional: bool = False,
        temporal_scale: float | int = None,
        temporal_units: str = "s") -> pd.DataFrame:
    
    if units == "um":
        
        units = "\u00b5m"
    
    if np.any(mask_array):
        
        if mask_array.ndim < im_array.ndim:
            
            mask_array = cc.project_mask(mask_array, im_array.shape[0])
    
    if not positional:
    
        if im_array.dtype != np.int64:
            
            lab_array = thresh.label(
                im_array,
                connectivity = connectivity,
                background = background)
            size_df: pd.DataFrame = __get_size_distribution(
                lab_array,
                mask_array = mask_array,
                mode = mode,
                diam_rad_mode = diam_rad_mode,
                pixel_size = pixel_size,
                units = units,
                background = background,
                normalize = normalize,
                nbins = nbins,
                max_bound = max_bound)
            
        else:
            
            size_df: pd.DataFrame = __get_size_distribution(
                im_array,
                mask_array = mask_array,
                mode = mode,
                diam_rad_mode = diam_rad_mode,
                pixel_size = pixel_size,
                units = units,
                background = background,
                normalize = normalize,
                nbins = nbins,
                max_bound = max_bound)
            
        return size_df
    
    else:
        
        if temporal_scale:
            
            pos_scale = temporal_scale
            pos_units = temporal_units
            
        else:
            
            pos_scale = pixel_size
            pos_units = units
            
        if im_array.dtype != np.int64:
            
            lab_array = thresh.label(
                im_array,
                connectivity = connectivity,
                background = background,
                positional = True)
            
        if mode == "vol":
            
            size_interval: float | int = pixel_size ** 3
            
        elif mode == "area":
            
            size_interval: float | int = pixel_size ** 2
            
        elif mode == "diam" or mode == "rad":
            
            size_interval: float | int = pixel_size
            
        columns = ["Size"]
            
        for slice_index in range(0, im_array.shape[0]):
            
            if im_array.dtype != np.int64:
                
                int_im_array = lab_array[slice_index]
                
            else:
                
                int_im_array = im_array[slice_index]
            
            if np.any(mask_array):
                
                int_df: pd.DataFrame = __get_size_distribution(
                    int_im_array,
                    mask_array = mask_array[slice_index],
                    mode = mode,
                    diam_rad_mode = diam_rad_mode,
                    pixel_size = pixel_size,
                    units = units,
                    background = background,
                    normalize = normalize,
                    nbins = nbins,
                    max_bound = max_bound)
            
            else:
                
                int_df: pd.DataFrame = __get_size_distribution(
                    int_im_array,
                    mode = mode,
                    diam_rad_mode = diam_rad_mode,
                    pixel_size = pixel_size,
                    units = units,
                    background = background,
                    normalize = normalize,
                    nbins = nbins,
                    max_bound = max_bound)
                
            columns.append(str(pos_scale * slice_index))
            int_sizes: np.ndarray = np.squeeze(
                np.array([int_df["Bin Centers"]]))
            int_counts: np.ndarray = np.squeeze(
                np.array([int_df["Counts"]]))
            
            if not int_sizes.shape:
                
                int_sizes = np.expand_dims(int_sizes, 0)
                int_counts = np.expand_dims(int_counts, 0)
            
            if slice_index == 0:
                
                size_array: np.ndarray = np.arange(
                    size_interval,
                    (np.max(int_sizes) + size_interval),
                    size_interval)
                size_array = np.expand_dims(size_array, 1)
                
            if size_array[0, 0] != int_sizes[0]:
                
                insert_array: np.ndarray = np.arange(
                    size_interval,
                    int_sizes[0],
                    size_interval)
                insert_zeros: np.ndarray = np.zeros(insert_array.shape)
                int_sizes = np.append(insert_array, int_sizes)
                int_counts = np.append(insert_zeros, int_counts)
            
            if size_array[-1, 0] > int_sizes[-1]:
                
                append_array: np.ndarray = np.arange(
                    (int_sizes[-1] + size_interval),
                    size_array[-1, 0] + size_interval,
                    size_interval)
                append_zeros: np.ndarray = np.zeros(append_array.shape)
                int_sizes = np.append(int_sizes, append_array)
                int_counts = np.append(int_counts, append_zeros)
            
            elif size_array[-1, 0] < int_sizes[-1]:
                
                stack_array: np.ndarray = np.expand_dims(
                    np.arange(
                        (size_array[-1, 0] + size_interval),
                        int_sizes[-1] + size_interval,
                        size_interval),
                    0)
                stack_zeros: np.ndarray = np.zeros(
                    ((size_array.shape[1] - 1),
                     stack_array.shape[1]))
                stack_array = np.vstack((stack_array, stack_zeros)).T
                size_array = np.vstack((size_array, stack_array))
                
            size_array = np.hstack((size_array, np.expand_dims(int_counts, 1)))
            
        size_df: pd.DataFrame = pd.DataFrame(size_array, columns = columns)
        
        if temporal_scale:
            
            size_df.attrs = {"time_units": pos_units}
            
        else:
            
            size_df.attrs = {"pos_units": pos_units}
        
        if mode == "vol":
                
            size_df.attrs["vol_units"] = f"{units}\u00b3"
                
        elif mode == "area":
    
            size_df.attrs["area_units"] = f"{units}\u00b2"
                    
        elif mode == "diam" or mode == "rad":
                
            size_df.attrs["diam_units"] = units
            
        return size_df

def get_time_series(
        im_array: np.ndarray,
        mode: str = "vol", *,
        mask_array: np.ndarray = None,
        size_mode: str = "area",
        pixel_size: float | int = 1.0,
        spatial_units: str = "pix",
        temporal_units: str = "s",
        temporal_scale: float | int = 1.0,
        connectivity: int = None,
        axis: int = 0,
        include_background: bool = False,
        background: float | int = 0,
        normalize: bool = False,
        norm_method: str = "total") -> pd.DataFrame:
    
    if spatial_units == "um":
        
        spatial_units = "\u00b5m"
    
    if mode == "size":
        
        time_df: pd.DataFrame = get_size_distribution(
            im_array,
            mask_array = mask_array,
            mode = size_mode,
            pixel_size = pixel_size,
            units = spatial_units,
            connectivity = connectivity,
            background = background,
            positional = True,
            temporal_scale = temporal_scale,
            temporal_units = temporal_units,
            normalize = normalize)
    
    else:
        
        time_df: pd.DataFrame = get_position_distribution(
            im_array,
            mode = mode,
            mask_array = mask_array,
            pixel_size = pixel_size,
            units = spatial_units,
            temporal_units = temporal_units,
            temporal_scale = temporal_scale,
            axis = axis,
            include_background = include_background,
            background = background,
            normalize = normalize,
            norm_method = norm_method)

    return time_df

def get_heat_map(
        im_array: np.ndarray,
        mode: str = "thickness", *,
        mask_array: np.ndarray = None,
        pixel_size: float = 1.0,
        axis: int = 0,
        height_orientation: str = "near") -> np.ndarray:
    
    if im_array.ndim == 2:
        
        return im_array
    
    else:
    
        if im_array.dtype != np.bool:
            
            bool_array: np.ndarray = pixels.convert_im_type(im_array, "bool")
            
        else:
            
            bool_array: np.ndarray = np.copy(im_array)
            
        if np.any(mask_array):
            
            if mask_array.ndim < im_array.ndim:
                
                mask_array = cc.project_mask(mask_array, im_array.shape[0])
            
            bool_array[np.logical_not(np.bool(mask_array))] = False
            
        if mode == "thickness":
            
            heat_array: np.ndarray = np.count_nonzero(bool_array, axis)
        
        elif mode == "height":
            
            if axis == 0:
                
                max_height_array: np.ndarray = np.ones(
                    (im_array.shape[1], im_array.shape[2])) * (im_array.shape[0] - 1)
                
            elif axis == 1:
                
                max_height_array: np.ndarray = np.ones(
                    (im_array.shape[0], im_array.shape[2])) * (im_array.shape[1] - 1)
            
            elif axis == 2:
                
                max_height_array: np.ndarray = np.ones(
                    (im_array.shape[0], im_array.shape[1])) * (im_array.shape[2] - 1)
            
            if height_orientation == "near":
                
                heat_array: np.ndarray = np.argmax(bool_array, axis)
            
            elif height_orientation == "far":
                
                heat_array: np.ndarray = max_height_array - np.argmax(
                    trans.mirror(bool_array, axis), axis)
                
        if axis == 0:
            
            heat_array = trans.mirror(heat_array, 0)
                
        if axis == 2:
    
            heat_array = trans.mirror(
                trans.mirror(
                    trans.rotate(
                        heat_array,
                        -90,
                        resize = True,
                        preserve_range = True),
                    0),
                1)
                
        return heat_array * pixel_size
    
def get_fractal_distrib(
        im_array: np.ndarray,
        pixel_size: float = 1,
        units: str = "pix",
        bounds: tuple = None,
        nbins: int = 10) -> pd.DataFrame:
    
    if units == "um":
        
        units = "\u00b5m"
        
    if bounds:
        
        nbins: np.ndarray = np.logspace(
            math.log10(bounds[0]),
            math.log10(bounds[1]),
            num = nbins)
    
    fractal_distrib: metrics.Results = metrics.boxcount(im_array, nbins)
    fractal_df: pd.DataFrame = pd.DataFrame(
        np.concat(
            (np.expand_dims(np.array(fractal_distrib.size), 1),
            np.expand_dims(np.array(fractal_distrib.slope), 1)),
            axis = 1
        ),
        columns = ["Pixel Size", "Fractal Dimension"]
    )
    fractal_df["Pixel Size"] *= pixel_size
    fractal_df.attrs["units"] = units
    
    return fractal_df


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()