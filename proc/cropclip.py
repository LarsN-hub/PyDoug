"""
Module for cropping, clipping, and padding image dimensions
"""

# Imports

import numpy as np

from skimage import draw


# Functions

def coords_2_lists(shape_coords: np.array) -> dict[str, list]:
    
    shape_coords = np.rint(shape_coords)
    rows: list[int] = []
    cols: list[int] = []
    
    for index, coords in enumerate(shape_coords):
        
        rows.append(int(coords[0]))
        cols.append(int(coords[1]))
        
    return {"rows": rows, "cols": cols}

def shape_mask_coords(shape_coords: np.array, shape_type: str) -> np.array:
    
    coords_dict: dict[str, list] = coords_2_lists(shape_coords)
    
    if shape_type == "rectangle":
        
        return draw.rectangle((min(coords_dict["rows"]), min(coords_dict["cols"])), (max(coords_dict["rows"]), max(coords_dict["cols"])))
    
    elif shape_type == "ellipse":
        
        pass

def crop(im_array: np.array, shape_type: str, shape_coords: np.array, *, outside_mask_intensity: int | float = 0) -> np.array:
    
    valid_shapes: tuple[str] = ("rectangle", "ellipse", "line")
    
    if any(shape_type.find(x) != -1 for x in valid_shapes):
        
        coords_dict: dict[str, list] = coords_2_lists(shape_coords)            
        crop_array: np.array = im_array[:, min(coords_dict["rows"]):max(coords_dict["rows"]), min(coords_dict["cols"]):max(coords_dict["cols"])]
        
        if len(set(coords_dict["rows"])) > 2:
            
            pass
        
        elif len(set(coords_dict["rows"])) == 2 and shape_type.find("ellipse") != -1:
            
            pass
            
        return crop_array
    
    else:
        
        print("\nInvalid shape type!")


# Main

def main() -> None:
    
    pass

if __name__ == "__main__":
    
    main()