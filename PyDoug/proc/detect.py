"""
Module for detection-based image segmentation
"""


# Imports

import numpy as np

from scipy import ndimage as ndi
from skimage import segmentation, filters, feature

from PyDoug.proc import cropclip as cc, pixels, util, morph, thresh
from PyDoug.analyze import quant


# Functions

def edge(im_array: np.ndarray, mask_array: np.ndarray = None, *,
         method: str = "sobel",
         sigma: float = 1.0,
         ksize: int = 3,
         alpha: float = 100,
         igg_sigma: float = 5,
         convert_type: bool = True,
         axis: int = None) -> np.ndarray:
    
    if np.any(mask_array):
        
        if mask_array.ndim < im_array.ndim:
            
            mask_array = cc.mask_2d_to_3d(mask_array, im_array.shape[0])
    
    if method == "sobel":
        
        edge_array: np.ndarray = filters.sobel(im_array, mask = mask_array, axis = axis)
    
    elif method == "canny":
        
        if len(im_array.shape) > 2:
        
            edge_array: np.ndarray = np.empty(im_array.shape)
            
            if np.any(mask_array):
            
                for slice_index in range(0, im_array.shape[0]):
            
                    edge_array[slice_index] = feature.canny(im_array[slice_index], sigma = sigma, mask = np.bool(mask_array[slice_index]), mode = "reflect")
                    
            else:
                
                for slice_index in range(0, im_array.shape[0]):
            
                    edge_array[slice_index] = feature.canny(im_array[slice_index], sigma = sigma, mode = "reflect")
                    
        else:
            
            edge_array = feature.canny(im_array, sigma = sigma, mask = mask_array, mode = "reflect")
    
    elif method == "farid":
        
        edge_array: np.ndarray = filters.farid(im_array, mask = mask_array, axis = axis)
        
    elif method == "igg":
        
        if np.any(mask_array):
            
            edge_array: np.ndarray = segmentation.inverse_gaussian_gradient(cc.mask(im_array, np.bool(mask_array)), alpha, igg_sigma)
        
        else:
        
            edge_array: np.ndarray = segmentation.inverse_gaussian_gradient(im_array, alpha, igg_sigma)
    
    elif method == "laplace":
        
        edge_array: np.ndarray = filters.laplace(im_array, ksize = ksize, mask = mask_array)
    
    elif method == "prewitt":
        
        edge_array: np.ndarray = filters.prewitt(im_array, mask = mask_array, axis = axis)
    
    elif method == "roberts":
        
        if len(im_array.shape) > 2:
        
            edge_array: np.ndarray = np.empty(im_array.shape)
            
            if np.any(mask_array):
            
                for slice_index in range(0, im_array.shape[0]):
            
                    edge_array[slice_index] = filters.roberts(im_array[slice_index], mask = np.bool(mask_array[slice_index]))
                    
            else:
                
                for slice_index in range(0, im_array.shape[0]):
            
                    edge_array[slice_index] = filters.roberts(im_array[slice_index])
                    
        else:
            
            edge_array = filters.roberts(im_array, mask = mask_array)
    
    elif method == "scharr":
        
        edge_array: np.ndarray = filters.scharr(im_array, mask = mask_array, axis = axis)
    
    if convert_type:
        
        return pixels.convert_im_type(edge_array, im_array.dtype)
    
    else:
        
        return edge_array
    
def level_set(array_shape: tuple, method: str = "checkerboard", *,
              square_size: int = 5,
              radius: float = 10) -> np.ndarray:
    
    if method == "checkerboard":
        
        return segmentation.checkerboard_level_set(array_shape, square_size)
        
    elif method == "disk":
        
        return segmentation.disk_level_set(array_shape, radius = radius)
    
def morph_snakes(im_array: np.ndarray, method: str = "ACWE", *,
                 square_size: int = 5,
                 radius: float = 10,
                 num_iter: int = 10,
                 smoothing: int = 1,
                 alpha: float = 100,
                 sigma: float = 5) -> np.ndarray:
    
    init_levels: np.ndarray = level_set(im_array.shape, square_size = square_size, radius = radius)
    
    if method == "ACWE":
        
        morph_array: np.ndarray = segmentation.morphological_chan_vese(im_array, num_iter = num_iter, init_level_set = init_levels, smoothing = smoothing)
    
    elif method == "GAC":
        
        morph_array: np.ndarray = segmentation.morphological_chan_vese(edge(im_array, method = "igg", alpha = alpha, sigma_2 = sigma, convert_type = False), num_iter = num_iter, init_level_set = init_levels, smoothing = smoothing)
        
    return pixels.convert_im_type(morph_array, "uint8", norm = True)

def random_walk(im_array: np.ndarray, marker_percentiles: tuple, beta: float = 130) -> np.ndarray:
    
    marker_ints: tuple = quant.get_percent_intensities(im_array, marker_percentiles)
    markers = np.zeros(im_array.shape, dtype = np.uint8)
    markers[im_array < min(marker_ints)] = 1
    markers[im_array > max(marker_ints)] = 2
    
    return pixels.normalize(segmentation.random_walker(im_array, markers, beta))

def watershed(im_array: np.ndarray, *,
              background: float | int = 0,
              mask_array: np.ndarray = None,
              water_line: bool = False,
              connectivity: int = 2,
              radius: int = 3,
              compactness: float = 0,
              along_axis: bool = False,
              axis: int = 0,
              randomize: bool = True) -> np.ndarray:
    
    if np.any(mask_array):
        
        if mask_array.ndim < im_array.ndim:
            
            mask_array = cc.project_mask(mask_array, im_array.shape[0])
            
        im_array[np.logical_not(np.bool(mask_array))] = background
        
    if im_array.dtype != np.bool:
        
        proc_array = np.bool(im_array)
        
    if im_array.ndim == 2:
        
        disk_footprint: morph.Footprint = morph.Footprint("disk")
        disk_footprint.radius: int = radius
        footprint: np.ndarray = disk_footprint.get_footprint()
        distance: np.ndarray = ndi.distance_transform_edt(proc_array)
        peak_coords: np.ndarray = feature.peak_local_max(distance, footprint = footprint, labels = proc_array)
        water_mask_array: np.ndarray = np.zeros(distance.shape, dtype = bool)
        water_mask_array[tuple(peak_coords.T)] = True
        markers: np.ndarray = thresh.label(water_mask_array)
        water_array: np.ndarray = segmentation.watershed(-distance, markers, connectivity = connectivity, compactness = compactness, mask = proc_array)
    
    elif along_axis:
        
        disk_footprint: morph.Footprint = morph.Footprint("disk")
        disk_footprint.radius: int = radius
        footprint: np.ndarray = disk_footprint.get_footprint()
        proc_array: np.ndarray = util.get_along_axis_array(proc_array, axis)
        water_array: np.ndarray = np.empty(proc_array.shape)
        
        for slice_index in range(0, proc_array.shape[0]):
            
            int_im_array: np.ndarray = proc_array[slice_index]
            distance: np.ndarray = ndi.distance_transform_edt(int_im_array)
            peak_coords: np.ndarray = feature.peak_local_max(distance, footprint = footprint, labels = int_im_array)
            water_mask_array: np.ndarray = np.zeros(distance.shape, dtype = bool)
            water_mask_array[tuple(peak_coords.T)] = True
            markers: np.ndarray = thresh.label(water_mask_array)
            water_array[slice_index] = segmentation.watershed(-distance, markers, connectivity = connectivity, compactness = compactness, mask = int_im_array)
            
        water_array = util.undo_axial_array(water_array, axis)
    
    else:
        
        ball_footprint: morph.Footprint = morph.Footprint("ball")
        ball_footprint.radius: int = radius
        footprint: np.ndarray = ball_footprint.get_footprint()
        distance: np.ndarray = ndi.distance_transform_edt(proc_array)
        peak_coords: np.ndarray = feature.peak_local_max(distance, footprint = footprint, labels = proc_array)
        water_mask_array: np.ndarray = np.zeros(distance.shape, dtype = bool)
        water_mask_array[tuple(peak_coords.T)] = True
        markers: np.ndarray = thresh.label(water_mask_array)
        water_array: np.ndarray = segmentation.watershed(-distance, markers, connectivity = connectivity, compactness = compactness, mask = proc_array)
    
    if randomize:
        
        return thresh.randomize_labels(water_array)
    
    else:
        
        return water_array

def corners(im_array: np.ndarray, method = "fast", *,
            n: int = 12,
            threshold: float = 0.15,
            harris_method: str = "k",
            k: int = 0.05,
            eps: int = 0.000001,
            sigma: float = 1,
            window_size: int = 1,
            correct_anomalies: bool = True,
            return_mode: str = "coords",
            orient_radius: int = 3,
            angles_radius: int = 5) -> np.ndarray:
    
    corner_array: np.ndarray = np.empty(im_array.shape)
        
    if method == "fast":
            
        if im_array.ndim > 2:
            
            for slice_index in range(0, im_array.shape[0]):
                
                corner_array[slice_index] = feature.corner_fast(im_array[slice_index], n, threshold)
                    
        else:
                
            corner_array = feature.corner_fast(im_array, n, threshold)
        
    elif method == "harris":
            
        if im_array.ndim > 2:
            
            for slice_index in range(0, im_array.shape[0]):
                
                corner_array[slice_index] = feature.corner_harris(im_array[slice_index], harris_method, k, eps, sigma)
                    
        else:
                
            corner_array = feature.corner_harris(im_array, harris_method, k, eps, sigma)
            
    elif method == "kitchen rosenfeld":
            
        if im_array.ndim > 2:
            
            for slice_index in range(0, im_array.shape[0]):
                
                corner_array[slice_index] = feature.corner_kitchen_rosenfeld(im_array[slice_index], "reflect")
                    
        else:
                
            corner_array = feature.corner_kitchen_rosenfeld(im_array, "reflect")
        
    elif method == "moravec":
            
        if im_array.ndim > 2:
            
            for slice_index in range(0, im_array.shape[0]):
                
                corner_array[slice_index] = feature.corner_moravec(im_array[slice_index], window_size)
                    
        else:
                
            corner_array = feature.corner_moravec(im_array, window_size)
        
    elif method == "shi tomasi":
            
        if im_array.ndim > 2:
            
            for slice_index in range(0, im_array.shape[0]):
                
                corner_array[slice_index] = feature.corner_shi_tomasi(im_array[slice_index], sigma)
                    
        else:
                
            corner_array = feature.corner_shi_tomasi(im_array, sigma)
            
    corner_coords: np.ndarray = feature.corner_peaks(corner_array)
    corner_array: np.ndarray = feature.corner_peaks(corner_array, indices = False)
    
    if correct_anomalies:
        
        if im_array.ndim == 2:
        
            for index, coords in enumerate(corner_coords):
                
                r0: int = max(coords[0] - 1, 0)
                r1: int = min(coords[0] + 2, im_array.shape[0])
                c0: int = max(coords[1] - 1, 0)
                c1: int = min(coords[1] + 2, im_array.shape[1])
                patch: np.ndarray = im_array[r0:r1, c0:c1]
                
                if np.unique(patch).shape[0] == 2:
                    
                    if index == 0:
                        
                        corrected_coords: np.ndarray = np.copy(coords)
                        
                    else:
                        
                        corrected_coords = np.vstack((corrected_coords, coords))
                        
                else:
                    
                    corner_array[coords[0], coords[1]] = 0
                
        else:
            
            for index, coords in enumerate(corner_coords):
                
                z0: int = max(coords[0] - 1, 0)
                z1: int = min(coords[0] + 2, im_array.shape[0])
                r0: int = max(coords[1] - 1, 0)
                r1: int = min(coords[1] + 2, im_array.shape[0])
                c0: int = max(coords[2] - 1, 0)
                c1: int = min(coords[2] + 2, im_array.shape[1])
                patch: np.ndarray = im_array[z0:z1, r0:r1, c0:c1]
                
                if np.unique(patch).shape[0] == 2:
                    
                    if index == 0:
                        
                        corrected_coords: np.ndarray = np.copy(coords)
                        
                    else:
                        
                        corrected_coords = np.vstack((corrected_coords, coords))
                        
                else:
                    
                    corner_array[coords[0], coords[1]] = 0
        
        corner_coords = np.copy(corrected_coords)
            
    if return_mode == "coords":
            
        return corner_coords
        
    elif return_mode == "peaks array":
            
        return pixels.convert_im_type(corner_array, "uint8")
    
    elif return_mode == "orients" or return_mode == "orients array":
        
        footprint: morph.Footprint = morph.Footprint("disk")
        footprint.radius = 3
        footprint_array: np.ndarray = footprint.get_footprint()
        
        if util.is_3d_rgb(im_array)["3D"]:
            
            orients_list: np.ndarray = np.zeros((1, 1))
            
            for slice_index in range(0, im_array.shape[0]):
                
                if np.any(corner_coords[corner_coords[:, 0] == slice_index]):
                    
                    orients_list = np.vstack((orients_list, np.expand_dims(feature.corner_orientations(im_array[slice_index], corner_coords[corner_coords[:, 0] == slice_index][:, 1:], footprint_array), 1)))
                    
            orients_list = orients_list[1:, :]
            
        else:
            
            orients_list: np.ndarray = feature.corner_orientations(im_array, corner_coords, footprint_array)
        
        if return_mode == "orients":
            
            return np.degrees(orients_list) + 180
        
        elif return_mode == "orients array":
            
            orients_array: np.ndarray = np.zeros(im_array.shape)
            orients_list = np.degrees(orients_list) + 180
            
            if im_array.ndim == 2:
                
                orients_array[corner_coords[:, 0], corner_coords[:, 1]] = orients_list[:, 0]
            
            else:
                
                orients_array[corner_coords[:, 0], corner_coords[:, 1], corner_coords[:, 2]] = orients_list[:, 0]
            
            return orients_array
        
def opening_angles(im_array: np.ndarray, min_size: int = 3) -> np.ndarray:
    
    edge_array: np.ndarray = morph.remove_objects(quant.get_contact(im_array, return_mode = "array"), min_size)
    edge_coords: np.ndarray = np.argwhere(edge_array)
    angles_array: np.ndarray = np.zeros(edge_array.shape)
    
    for coords in edge_coords:
        
        r0: int = max(coords[0] - 1, 0)
        r1: int = min(coords[0] + 2, edge_array.shape[0])
        c0: int = max(coords[1] - 1, 0)
        c1: int = min(coords[1] + 2, edge_array.shape[0])
        local_r: int = coords[0] - r0
        local_c: int = coords[1] - c0
        patch: np.ndarray = np.copy(edge_array[r0:r1, c0:c1])
        patch[local_r, local_c] = 0
        indices: np.ndarray = np.argwhere(patch)
        vecs: np.ndarray = indices - np.repeat(np.array([[1, 1]]), indices.shape[0], axis = 0)
        magnitudes: np.ndarray = np.sqrt(np.sum((vecs ** 2), axis = 1))
        
        if np.count_nonzero(patch) == 2:
            
            vec1: np.ndarray = indices[0, :] - np.array([local_r, local_c])
            vec2: np.ndarray = indices[1, :] - np.array([local_r, local_c])
            
        elif np.count_nonzero(patch) > 2 and np.count_nonzero(magnitudes == 1) == 2:
            
            target_indices: np.ndarray = np.squeeze(indices[np.argwhere(magnitudes == 1), :])
            vec1: np.ndarray = target_indices[0, :] - np.array([local_r, local_c])
            vec2: np.ndarray = target_indices[1, :] - np.array([local_r, local_c])
            
        else:
                
            vec1: np.ndarray = np.array([0, 1])
            vec2: np.ndarray = np.array([0, 1])
        
        angle: int = round(np.degrees(np.arccos(np.dot(vec1, vec2) / (np.sqrt(np.sum(vec1 ** 2)) * np.sqrt(np.sum(vec2 ** 2))))))
        
        if angle == 45:
            
            test_coords: np.ndarray = coords - vec1
            
            if test_coords[0] < im_array.shape[0] and test_coords[1] < im_array.shape[1]:
            
                if im_array[test_coords[0], test_coords[1]] == 0:
                
                    angle: int = 315
        
        elif angle == 90:
            
            test_coords: np.ndarray = coords + vec1 + vec2
            
            if test_coords[0] < im_array.shape[0] and test_coords[1] < im_array.shape[1]:
            
                if im_array[test_coords[0], test_coords[1]] == 0:
                
                    angle: int = 270
        
        elif angle == 135:
            
            test_coords: np.ndarray = coords + vec1 + vec2
            
            if test_coords[0] < im_array.shape[0] and test_coords[1] < im_array.shape[1]:
            
                if im_array[test_coords[0], test_coords[1]] == 0:
                
                    angle: int = 225
                
        angles_array[coords[0], coords[1]] = angle
        
    return angles_array
                

# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()