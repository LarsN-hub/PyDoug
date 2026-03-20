-------
Preface
-------

I am not a software developer. I am a PhD candidate who knows some things about image processing
and wanted to make a GUI-operated resource for people who may not have access to MATLAB or ORS Dragonfly
due to monetary or licensing limitations. Please be patient with me as I navigate through the world
of coding and GitHub best practices, licensing, and all that jazz.

I have only ever used Windows systems, so I cannot say whether or not this works on Linux or Apple
systems nor can I currently provide support for installing this on those systems.

I am working on figuring out how to make this a single, downloadable executable file, but this has
proven more difficult than I realized. Until then, installing PyDoug will require a few more steps
as explained below.

---------
Resources
---------

PyDoug is built completely in Python: https://www.python.org/

The GUI is built on napari's n-dimensional image viewing GUI: https://napari.org/stable/

Widgets were added to the napari GUI with magicgui: https://pyapp-kit.github.io/magicgui/
and magic-class: https://hanjinliu.github.io/magic-class/

Most widgets are wrapper functions for functions from the scikit-image library: https://scikit-image.org/,
numpy: https://numpy.org/, scipy: https://scipy.org/, matplotlib: https://matplotlib.org/, and
algotom: https://myalgotomo.readthedocs.io/en/latest/index.html

Other miscellaneous resources used:
- h5py: https://docs.h5py.org/en/stable/index.html
- numba: https://numba.pydata.org/
- pandas: https://pandas.pydata.org/
- PyQt5: https://pypi.org/project/PyQt5/
- QtPy: https://pypi.org/project/QtPy/
- tkinter_unblur: https://pypi.org/project/tkinter-unblur/

---------------------
Installing & Updating
---------------------

**Windows Installation**
1. Ensure that Python v3.13 is installed on your computer.
2. Test that you have it by opening Windows PowerShell and typing "python".
   - If it worked, some information about python (3.13._) should pop up and the input line should have
     ">>>" in front of it.
   - If this is the case, type quit() to exit python and proceed. If this did not
     happen, do not continue with this process and figure this out first.
3. Navigate to the Tags section in releases as I am frequently fixing bugs during the alpha phase.
4. Download the .zip file for the most recent tag/release.
5. Extract the contents wherever you please.
6. Navigate inside the extracted folder. You should see a folder named "PyDoug" and several text documents.
7. Move the PyDoug folder and the requirements_dist.txt file to your user folder (e.g. C:\Users\Your_Name)
   - Note, you may place these wherever you want but this is the simplest option and I will only provide
     guidance for installation from this folder.
   - If you are knowledgeable enough, then changing the commands that follow to a different folder should
     not be too difficult.
8. Open Windows Powershell if not already open from before.
9. It should open in C:\Users\Your_Name by default, but if not type 'cd "C:\Users\Your_Name"' then enter.
   - Note that "Your_Name" is the folder where you moved PyDoug and requirements_dist.txt to previously.
10. Type 'python -m venv PyDoug_Env' then enter.
11. Once it is finished, type 'PyDoug_Env\Scripts\pip install -r requirements_dist.txt' then enter.
    - Note, this will take some time. Allow it to install everything before doing anything else.
12. Once it is finished, type 'PyDoug_Env\Scripts\python -m PyDoug' to launch PyDoug.
    - Note, the napari GUI may take a minute to launch. It is normal for it to flash many small popups
     during this process.
13. If this worked and PyDoug launches successfully, you need only launch Windows PowerShell and re-enter
    the above command 'PyDoug_Env\Scripts\python -m PyDoug' to launch PyDoug every time (assuming that you
    launch PowerShell in the C:\Users\Your_Name folder where the PyDoug folder is located).

**Update**
1. Download the .zip file for the most recent tag/release.
2. Extract the contents wherever you please.
3. Navigate inside the extracted folder. Move the folder named "PyDoug" to the location of your current PyDoug folder.
4. Allow it to replace all current files.

------------
General Info
------------

When you launch PyDoug, you will see the napari gui with a list of widget tabs on the right side. The widgets area can
be un-docked and moved around for your convenience. However, DO NOT close the widgets tab or you will need to restart
the program to get them back. Aside from the widgets area, everything with any imported image files works according to napari's
website: https://napari.org/stable/tutorials/fundamentals/quick_start.html. I recommend familiarizing yourself with how
napari works for ease of use with PyDoug. Here are some general instructions:

- Any single image file (other than .h5-type formats) can simply be dragged and dropped into the napari window to open.
- You can move the image around by clicking and dragging with the mouse.
- Toggle between 2D/3D view with the second from the left button at the bottom left of the gui.
- Toggle visibility of any imported image with the eyeball icon to the left of its name in the layer list (lower left).
- Open up visibility settings for any image layer by clicking on it (they appear above it, in the upper left).
- Delete any image layer by clicking on it and hitting the trashcan icon.
- All widgets can be collapsed by clicking on their name box (contains a triangle in front of the name as indication).

Buttons/functionality native to napari that you should NOT use in PyDoug:
- The points, shapes, or labels layer creation buttons (immediately above the layers list)
- The axis transpose buttons (bottom left, immediately right of the 2D/3D button)
- The image layer renaming feature (activated by double-clicking on a layer's name)

PyDoug has its own functionality for shapes and labels that napari handles differently. Additionally, transposing axes
with napari's buttons rather than PyDoug's reslice widget will not record what you have done in the constantly-updating
parameters log, meaning you cannot recreate those transpositions in any later batch processing if needed. Finally, chaning
a layer's name will not update the parameters log, so if you remove the image later the parameters log will not be able
to find the operation to remove. Otherwise, these buttons will not "break" PyDoug, just potentially harm its functionality.

Whenever you modify an image with one of PyDoug's widgets, a parameters log will update with the operation performed and
the parameters used for the operation. When you delete an image layer from the layers list, the parameters log will delete
the entry corresponding to that layer's name. By exporting these parameters, you can use them for batch processing of
other datasets without you having to manually do so for each image.

**Shapes Layer**

After adding a shape (covered in the Masking Tab), the shapes layer can be interacted with by clicking on it in the layer list.
Use the hollow cursor option (not the filled cursor) to move shapes around. Drag a shape's vertices to change its dimensions.
Hold shift when changing dimensions to maintain the current aspect ratio. Click on a shape to change its appearance in the layer
controls window above the layer list window (opacity, edge width, edge color, etc.). Do not add shapes from this selection
window or they will only occupy a single slice of a stack as opposed to all slices of a stack when the add shape widget is used.
More info here: https://napari.org/stable/howtos/layers/shapes.html.

**Labels Layer**

After adding a labels layer (covered in the Masking Tab), the labels layer can be interacted with by clicking on it in the layer list.
Use the paintbrush option to draw on the image. The brush size can be altered and drawing in 2D or 3D can be performed. Change the label
index to change the color. Note that all label colors will be converted to the white portion of the mask (if painting a mask). Use the
paint-fill bucket to color an entire image/slice or within a pre-drawn boundary. DO NOT try to paint fill in 3D or the program will
almost certainly crash. Use the eraser option to remove previously drawn labels.
More info here: https://napari.org/stable/howtos/layers/labels.html.

-------
Widgets
-------

I/O Tab
-------
A tab containing widgets related to the import and export of datasets and batch processing operation / parameters.

**Import File**

A widget for importing single image files (2D or 3D). You can just drag and drop single tiff/png/jpeg type files
into the napari window if desired, but they can also be imported here. This widget can also import h5-type files
and (theoretically) any file that the Pillow library can handle: https://pillow.readthedocs.io/en/stable/handbook/tutorial.html.
- "File Path": click "Select file" to open a file selector dialog to locate the file.
- "Import File" button: click to import the file.

**Import File Sequence**

A widget for importing sequences of files contained in a folder.
- "Directory Path": click "Choose directory" to open a directory selector dialog to locate the folder containing the images.
- "Import File Sequence" button: click to import the file sequence.

**Export Image(s)**

A wiget for exporting images (2D or 3D).
- "Image" drop-down: images in the layer list. Select the image to export.
- "Method" drop-down: available export formats (tiff or hdf5)
- "Multi Page" checkbox: leave checked if "Method" is "Tiff" to export as multi-page (3D) tiff. Otherwise exports as tiff sequence.
  Has no functionality if "Method" is "HDF5".
- "Save Folder": click "Choose directory" to open a directory selector dialog to locate the save folder. Note that a folder will
  be created in this folder if exporting as a tiff sequence.
- "Save Name": type in a name for the exported image(s). This will be the name of the folder if exporting as a tiff sequence.
- "Export Image(s)" button: click to export the image(s).

**Export Parameters**

A widget for exporting the current parameters log.
- "Save Folder": click "Choose directory" to open a directory selector dialog to locate the save folder. Note that a folder will
  be created in this folder with the name provided in "Folder Name".
- "Folder Name": type in a name for the parameters folder.
- "Compress Masks" checkbox: leave checked to convert any masks used to 2D slices of their original 3D volume (if processing 3D images).
  If a mask has the same shape throughout every slice, this can save on storage space. If a mask has a unique shape on different slices,
  DO NOT leave this checked.
- "Export Parameters" button: click to export the parameters.

**Batch Processing**

A widget for batch processing other image(s) with an exported parameters log (parameters must be exported and saved already).
- "Image Format" drop-down: select "Stacks" if importing image sequences, otherwise select "Singles" for 2D images or multi-page (3D) tiffs.
- "Stack Format" drop-down: if "Image Format" is "Stacks", select "Multi-Page" if stacks are multi-page (3D) tiffs or hdf5-type files.
  Otherwise, select "Sequence" to import folders containing image sequences.
- "Export Images" checkbox: leave checked to export the images after processing. Uncheck if you are just creating plots from the images.
- "Export Multi Page" checkbox: leave checked to export stacks as multi-page (3D) tiffs. Uncheck to export stacks as image sequences.
- "Copy Parameters" checkbox: leave checked to put a copy of the parameters used in the export folder.
- "Run Batch Script" button: click to open the images selection dialog, followed by the parameters selection dialog, followed by the export
  selection dialog, followed by the batch script itself.

Manipulate Tab
--------------
A tab containing widgets that modify the dimensions of images.

**Trim / Pad**

A widget for removing (trimming) or adding (padding) specific amounts from/to each axis of an image.
- "Image" drop-down: images in the layer list. Select the image to trim/pad.
- "Method" drop-down: select "Trim" to remove from each axis. Select "Pad" to add to each axis.
- "Bounds as Slices" checkbox:
   - Trim: leave checked to enter slice range to keep. Un-check to enter specific number of pixels to trim from each axis.
   - Pad: leave checked to enter dimensions to expand image to. Un-check to enter specific number of pixels to add to each axis.
- "X Bounds" checkbox: leave checked to affect the X axis with "X Min" and "X Max". Un-check to leave X axis untouched.
- "X Min" integer:
   - Trim: if "Bounds as Slices" is checked, enter pixel column number left-of-which all columns will be removed. If "Bounds
     as Slices" is unchecked, enter number of pixel columns to remove from the left of the image.
   - Pad: if "Bounds as Slices" is checked, this value is ignored. If "Bounds as Slices" is unchecked, enter number of pixel
     columns to add to the left of the image.
- "X Max" integer:
   - Trim: if "Bounds as Slices" is checked, enter pixel column number right-of-which all columns will be removed. If "Bounds
     as Slices" is unchecked, enter number of pixel columns to remove from the right of the image.
   - Pad: if "Bounds as Slices" is checked, enter dimension to expand X axis to meet. If "Bounds as Slices" is unchecked, enter number
     of pixel columns to add to the right of the image.
- "Y Bounds" checkbox: leave checked to affect the Y axis with "Y Min" and "Y Max". Un-check to leave Y axis untouched.
- "Y Min" integer:
   - Trim: if "Bounds as Slices" is checked, enter pixel row number above-which all rows will be removed. If "Bounds
     as Slices" is unchecked, enter number of pixel rows to remove from the top of the image.
   - Pad: if "Bounds as Slices" is checked, this value is ignored. If "Bounds as Slices" is unchecked, enter number of pixel
     rows to add to the top of the image.
- "Y Max" integer:
   - Trim: if "Bounds as Slices" is checked, enter pixel row number below-which all rows will be removed. If "Bounds
     as Slices" is unchecked, enter number of pixel rows to remove from the bottom of the image.
   - Pad: if "Bounds as Slices" is checked, enter dimension to expand Y axis to meet. If "Bounds as Slices" is unchecked, enter number
     of pixel rows to add to the bottom of the image.
- "Z Bounds" checkbox: leave checked to affect the Z axis with "Z Min" and "Z Max". Un-check to leave Z axis untouched. No effect if the
  image is not 3D.
- "Z Min" integer:
   - Trim: if "Bounds as Slices" is checked, enter pixel slice number before-which all slices will be removed. If "Bounds
     as Slices" is unchecked, enter number of pixel slices to remove from the front of the stack.
   - Pad: if "Bounds as Slices" is checked, this value is ignored. If "Bounds as Slices" is unchecked, enter number of pixel
     slices to add to the front of the stack.
- "Z Max" integer:
   - Trim: if "Bounds as Slices" is checked, enter pixel slice number after-which all slices will be removed. If "Bounds
     as Slices" is unchecked, enter number of pixel slices to remove from the back of the stack.
   - Pad: if "Bounds as Slices" is checked, enter dimension to expand Z axis to meet. If "Bounds as Slices" is unchecked, enter number
     of pixel slices to add to the back of the stack.
- "Padded Color" drop-down: select the default color to assign to pixels added by padding.
- "Specify Color" checkbox: leave unchecked to use default "Padded Color". Check to specify a color in "Color Value".
- "Color Value" float: enter specific intensity value to assign to pixels added by padding.
- "Conserve RAM" checkbox: leave unchecked to create a new image layer from this operation. Check to overwrite the current image layer.
  If left checked, it is impossible to get the previous image back but a new array is not created, saving memory.
- "Trim / Pad" button: click to perform the trim or pad operation.

**Crop**

A widget for cropping an image using a pre-made mask (covered in Masking Tab).
- "Image" drop-down: images in the layer list. Select the image to crop.
- "Mask" drop-down: images in the layer list. Select the mask to use to crop "Image".
- "Masked Color" drop-down: select the default color to assign to pixels outside of the mask but within the new image
  (e.g. in the case of a circular crop)
- "Specify Color" checkbox: leave unchecked to use default "Masked Color". Check to specify a color in "Color Value".
- "Color Value" float: enter specific intensity value to assign to masked pixels remaining after cropping.
- "Conserve RAM" checkbox: leave unchecked to create a new image layer from this operation. Check to overwrite the current image layer.
  If left checked, it is impossible to get the previous image back but a new array is not created, saving memory.
- "Crop" button: click to perform the crop operation.

**Split**

A widget for splitting an image (or stack) into two separate layers at a certain column/row/slice.
Note, splitting will not go in the parameter log and cannot be performed in batch processing.
- "Image" drop-down: Images in the layer list. Select the image to split.
- "Split Index" integer: column, row, or slice at which to split the image or stack at.
- "Axis" drop-down: select the axis to split the image or stack on.
- "Split" button: click to perform the split operation.

**Join**

A widget for joining two images or stacks on a specified axis.
Note, joining will not go in the parameter log and cannot be performed in batch processing.
- "Image 1" drop-down: images in the layer list. Select the first image to join. This will be earlier on the specified axis.
- "Image 2" drop-down: images in the layer list. Select the second image to join. This will be later on the specified axis.
- "Axis" drop-down: select the axis to join the images or stacks on.
- "Join" button: click to perform the join operation.

**Extend**

A widget for duplicating an image along the Z axis.
- "Image" drop-down: images in the layer list. Select the image to extend.
- "Slice Count" integer: enter the number of slices that the new stack should have.
- "Add as Parameter" checkbox: check to add this operation to the parameter log for batch processing.
- "Extend" button: click to perform the extend operation.

Transform Tab
-------------
A tab containing widgets that perform geometric/matrix transformations on images.

**Reslice**

A widget for reslicing a stack to observe from a different direction. Treats the stack as a cube to be rotated.
- "Image" drop-down: images in the layer list. Select the image stack to reslice.
- "Orientation" drop-down: select the direction to view the stack cube from.
- "Reslice" button: click to perform the reslice operation.

**Rotate**

A widget for rotating an image or stack around the center of the Z axis.
More info: https://scikit-image.org/docs/stable/api/skimage.transform.html#skimage.transform.rotate
- "Image" drop-down: images in the layer list. Select the image to rotate.
- "Clockwise" checkbox: check to rotate clockwise. Leave unchecked to rotate counter clockwise.
- "Resize" checkbox: leave unchecked to keep original image dimensions. Check to expand dimensions outwards to avoid cropping
  off edges that are rotated out-of-frame.
- "Angle" float: enter the angle to rotate the image(s) by.
- "Rotate" button: click to perform the rotate operation.

**Mirror**

A widget for mirroring (flipping) an image or stack along an axis.
- "Image" drop-down: images in the layer list. Select the image to mirror.
- "Direction" drop-down: select the axis direction to flip the image / stack along.
- "Mirror" button: click to perform the mirror operation.

**Rescale**

A widget for rescaling pixels (image) or voxels (stack).
More info: https://scikit-image.org/docs/stable/api/skimage.transform.html#skimage.transform.rescale
- "Image" drop-down: images in the layer list. Select the image to rescale.
- "Scale" float: enter the scale by which to downsize (<1) or upsize (>1) the image.
- "Rescale" button: click to perform the rescale operation.

Masking Tab
-----------
A tab containing widgets that can create and apply masks to images.

**Mask**

A widget for masking an image using a pre-made mask.
- "Image" drop-down: images in the layer list. Select the image to mask.
- "Mask" drop-down: images in the layer list. Select the mask to use.
- "Mask Method" drop-down: select "Out" to mask pixels in the black area of the mask. Select "in" to mask pixels in the white area.
- "Masked Color" drop-down: select the default color to assign to masked pixels.
- "Specify Color" checkbox: leave unchecked to use default "Masked Color". Check to specify a color in "Color Value".
- "Color Value" float: enter specific intensity value to assign to masked pixels.
- "Mask" button: click to perform the mask operation.

**Add Shape**

A widget for creating a shapes layer if not already present and then add shapes to it. Modifying shapes is covered in General Info.
Note, adding shapes will not go in the parameter log and cannot be performed in batch processing.
- "Shape Type" drop-down: select the type of shape to add.
- "Polygon Vertices" integer: enter the number of vertices that a polygon select in "Shape Type" should have (min. 3).
- "Add Shape" button: click to add the currently selected shape.

**Create Mask from Shapes**

A widget for creating a mask from a shapes layer.
Note, creating a mask will not go in the parameter log and cannot be performed in batch processing.
- "Image" drop-down: images in the layer list. Select the image to make a mask with matching dimensions.
- "Shapes" drop-down: shapes in the layer list. Select the shapes layer to make the mask from.
- "Specify Slice Range" checkbox: check to only apply the shapes to the mask in a specified slice range. Leave unchecked to fill all
  slices with the shapes. Has no effect on 2D images.
- "Slice Start" integer: enter the slice to start applying the shapes to the mask if "Specify Slice Range" is checked.
- "Slice End" integer: enter the slice to stop applying the shapes to the mask if "Specify Slice Range" is checked.
- "Create Mask" button: click to create the mask.

**Paint**

A widget for creating a labels layer for painting. Painting in the labels layer is covered in General Info.
Note, painting will not go in the parameter log and cannot be performed in batch processing.
- "Image" drop-down: images in the layer list. Select the image to make a label layer with matching dimensions.
- "Paint" button: click to create the labels layer for painting.

**Create Mask from Paint**

A widget for creating a mask from a labels layer.
Note, creating a mask will not go in the parameter log and cannot be performed in batch processing.
- "Paint" drop-down: label layers in the layer list. Select the paint labels layer to make a mask.
- "Create Mask" button: click to create the mask.

**Mask Logic Operations**

A widget for PowerPoint-style shape merging operations.
Note, mask logic will not go in the parameter log and cannot be performed in batch processing.
- "Mask 1" drop-down: images in the layer list. Select the first mask for the merging operation.
- "Mask 2" drop-down: images in the layer list. Select the second mask for the merging operation.
- "Method" drop-down: select "Union" to make all white areas in each mask white. Select subtract to subtract the white areas
  in the second mask from those in the first mask. Select "intersect" to make only the areas that are white in each mask white.
- "Perform Operation" button: click to perform the mask logic operation.

Pixel Values Tab
----------------
A tab containing widgets that alter the bit-dpeth and intensity values of pixels.

**Convert Type**

A widget for converting the data type of images.
More info: https://scikit-image.org/docs/stable/api/skimage.util.html#skimage.util.img_as_bool,
https://scikit-image.org/docs/stable/api/skimage.util.html#skimage.util.img_as_float,
https://scikit-image.org/docs/stable/api/skimage.util.html#skimage.util.img_as_float32,
https://scikit-image.org/docs/stable/api/skimage.util.html#skimage.util.img_as_float64,
https://scikit-image.org/docs/stable/api/skimage.util.html#skimage.util.img_as_int,
https://scikit-image.org/docs/stable/api/skimage.util.html#skimage.util.img_as_ubyte,
https://scikit-image.org/docs/stable/api/skimage.util.html#skimage.util.img_as_uint
- "Image" drop-down: images in the layer list. Select the image to convert.
- "Type" drop-down: data type options for conversion.
- "Auto-Normalize" checkbox: leave checked to normalize the intensity values to the full width of the new type's range after conversion.
  This has no effect when converting between integer data types.
- "Bounds" checkbox: check to specify the bounds to normalize between if "Auto-Normalize" is checked.
- "Min" float: input minimum bound for normalization if "Bounds" checked.
- "Max" float: input maximum bound for normalization if "Bounds" checked.
- "Convert Type" button: click to perform the type conversion operation.

**Normalize**

A widget for normalizing the intensity range of images to a new range. This operation can be performed automatically for the
data type range of an image in the "Saturate" and "Convert Type" widgets.
More info: https://scikit-image.org/docs/stable/api/skimage.exposure.html#skimage.exposure.rescale_intensity
- "Image" drop-down: images in the layer list. Select the image to normalize.
- "Input Range" checkbox: check to specify an input range to normalize. Values outside this range will be clipped (as in saturation).
  If unchecked, the current range of the image will be used.
- "Input Min" float: specify the input range minimum if "Input Range" is checked.
- "Input Max" float: specify the input range maximum if "Input Range" is checked.
- "Output Range" checkbox: check to specify an output range for normalization. If unchecked, the range of the image's data type will be used.
- "Output Min" float: specify the output range minimum if "Output Range" is checked.
- "Output Max" float: specify the output range maximum if "Output Range" is checked.
- "Normalize" button: click to perform the normalization operation.

**Saturate**

A widget for clipping the image's histogram at extreme intensity values. Contrast can then be enhanced by normalizing.
- "Image" drop-down: images in the layer list. Select the image to saturate.
- "Auto-Normalize" checkbox: leave checked to normalize the intensity values to the full width of the image's data type's range after saturation.
- "Bounds as Percentages": leave checked to input the saturation bounds as percentages of the total image pixels. Uncheck to input specific
  intensity values. Regardless of the option used, the parameters log will record the specific intensity values used for consistency in batch
  processing. Note that leaving checked will require a calculation that may take some time depending on the image dimensions.
- "Min Bound" float: input the minimum bound for saturation.
- "Max Bound" float: input the maximum bound for saturation.
- "Apply Mask" checkbox: check to apply a mask to the image during saturation. Pixels that are masked will not be considered in the calculation
  of bounds percentages. This has no effect if "Bounds as Percentages" is unchecked.
- "Mask" drop-down: images in the layer list. Select the mask to be applied if "Apply Mask" is checked.
- "Saturate" button: click to perform the saturation operation.

**Equalize Histogram**

A widget for enhancing image contrast by equalizing the histogram (making brighter areas brighter and darker areas darker).
More info: https://scikit-image.org/docs/stable/api/skimage.exposure.html#skimage.exposure.equalize_hist,
https://scikit-image.org/docs/stable/api/skimage.exposure.html#skimage.exposure.equalize_adapthist,
https://scikit-image.org/docs/stable/api/skimage.filters.rank.html#skimage.filters.rank.equalize
- "Image" drop-down: images in the layer list. Select the image to equalize.
- "Method" drop-down: select the equalization method. "Global" takes all pixel values into account whereas "Local" and "Adaptive" consider only the surrounding
  neighborhood of pixels.
- "Local Radius" integer: input the radius to be used if "Method" is "Local".
- "Along Axis" checkbox: check to apply the operation along an axis of an image stack.
- "Axis" drop-dpown: select the axis to apply the operation along if "Along Axis" is checked.
- "Apply Mask" checkbox: check to apply a mask to the image during equalization. Pixels that are masked will not be considered in the equalization calculation.
- "Mask" drop-down: images in the layer list. Select the mask to be applied if "Apply Mask" is checked.
- "Equalize Histogram" button: click to perform the equalization operation.

**Invert**

A widget for inverting the intensity values of images within the data type's range (bright becomes dark and vice versa).
More info: https://scikit-image.org/docs/stable/api/skimage.util.html#skimage.util.invert
- "Image" drop-down: images in the layer list. Select the image to invert.
- "Invert" button: click to perform the inversion operation.

**Re-Assign Intensities**

A widget for assigning specific intensity values to new intensity values.
- "Image" drop-down: images in the layer list. Select the image to re-assign.
- "Input Intensity" float: input the intensity to be re-assigned.
- "Output Intensity" float: input the intensity to re-assign "Input Intensity" to.
- "Re-Assign" button: click to perform the re-assign operation.

**RGB to Grayscale**

A widget for converting RGB images to grayscale.
More info: https://scikit-image.org/docs/stable/api/skimage.color.html#skimage.color.rgb2gray
- "Image" drop-down: images in the layer list. Select the RGB image to convert to grayscale.
- "Grayscale" button: click to perform the RGB to grayscale operation.

Denoising Tab
-------------
A tab containing widgets that apply denoising filters to images.

**Bilateral Filter**

A widget for applying a bilateral filter to an image/stack. A bilateral filter is an edge-preserving smoothing filter.
Note that the bilateral filter can only be applied along an axis in 3D.
More info: https://scikit-image.org/docs/stable/api/skimage.restoration.html#skimage.restoration.denoise_bilateral
- "Image" drop-down: images in the layer list. Select the image to filter.
- "Axis" drop-down: select the axis along which the filter will be applied. This has no effect on a 2D image.
- "Window Size" integer: input the window size of the local filter. Leave as 0 for automatic calculation.
- "Sigma Color" float: input the standard deviation of the grayscale intensities to be smoothed. Leave as 0 for automatic calculation.
- "Sigma Spatial" float: input the standard deviation of the range distance for edge detection.
- "Bins" integer: larger value = higher accuracy for Gaussian weights color filtering.
- "Edges Method" drop-down: select the method for handling pixels on the edge of the image.
- "Constant Value" float: input the value to be used if "Edges Method" is "Constant".
- "Filter" button: click to perform the filter operation.

**Gaussian Blur**

A widget for applying a gaussian blur filter to an image/stack. A gaussian blur is a smoothing filter that does not preserve edges.
More info: https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.gaussian
- "Image" drop-down: images in the layer list. Select the image to filter.
- "Sigma" float: input the standard deviation for the Gaussian kernel (higher = smoother).
- "Truncate" float: input the number of standard deviations after which the filter in truncated.
- "Edges Method" drop-down: select the method for handling pixels on the edge of the image.
- "Constant Value" float: input the value to be used if "Edges Method" is "Constant".
- "Along Axis" checkbox: check to apply the operation along an axis of an image stack.
- "Axis" drop-dpown: select the axis to apply the operation along if "Along Axis" is checked.
- "Filter" button: click to perform the filter operation.

**Non-Local Means Filter**

A widget for applying a non-local means filter to an image/stack. A non-local means filter is an edge-preserving smoothing filter.
Note that this filter is very slow with image stacks.
More info: https://scikit-image.org/docs/stable/api/skimage.restoration.html#skimage.restoration.denoise_nl_means
- "Image" drop-down: images in the layer list. Select the image to filter.
- "Patch Size" integer: input the size of the non-local means kernel.
- "Patch Distance" integer: input the radius around pixels where other patches can be searched for.
- "Cut Off Distance" float: input the distance in gray value above which other patches are not accepted (higher = smoother).
- "Sigma" float: input the standard deviation of the Gaussian noise. Leave as 0 for automatic calculation.
- "Along Axis" checkbox: check to apply the operation along an axis of an image stack.
- "Axis" drop-dpown: select the axis to apply the operation along if "Along Axis" is checked.
- "Filter" button: click to perform the filter operation.

**Remove Background**

A widget for removing background from an image/stack. This filter will attempt to identify foreground from background and smooth the background.
More info: https://scikit-image.org/docs/stable/api/skimage.restoration.html#skimage.restoration.rolling_ball
- "Image" drop-down: images in the layer list. Select the image to filter.
- "Radius" integer: input the radius of the rolling ball used to find the background of the image.
- "Filter" button: click to perform the filter operation.

**Ring Removal**

A widget for applying a ring-removal filter to an image/stack. These filters attempt to smooth radial ring artifacts typically seen in XCT data.
Note, images must be perfectly square along the "Square Axis".
More info: https://myalgotomo.readthedocs.io/en/latest/api/algotom.post.postprocessing.html#algotom.post.postprocessing.remove_ring_based_fft,
https://myalgotomo.readthedocs.io/en/latest/api/algotom.post.postprocessing.html#algotom.post.postprocessing.remove_ring_based_wavelet_fft
- "Image" drop-down: images in the layer list. Select the image to filter.
- "Method" drop-down: select the ring-removal method to be used.
- "FFT Freq Cutoff" integer: if "Method" is "FFT", input the frequency cutoff.
- "FFT Filter Order" integer: if "Method" is "FFT", input the filter order.
- "FFT Rows" integer: if "Method" is "FFT", input the number of rows to apply the filter on.
- "Wavelet" drop-down: if "Method" is "Wavelet", select the wavelet to use for wavelet domain conversion.
- "Wavelet Level" integer: if "Method" is "Wavelet", input the wavelet decomposition level.
- "Wavelet Damping Size" intger: if "Method" is "Wavelet", input the wavelet damping size.
- "Sorting" checkbox: if checked, apply a sorting algorithm to potentially enhance strip removal (more computationally expensive).
- "Square Axis" drop-down: select the axis to apply the operation along (must be perfectly square).
- "Filter" button: click to perform the filter operation.

**TV Bregman Filter**

A widget for applying a total variation Bregman filter to an image/stack. A TV Bregman filter attempts to smooth an image while remaining similar
to the original image.
More info: https://scikit-image.org/docs/stable/api/skimage.restoration.html#skimage.restoration.denoise_tv_bregman
- "Image" drop-down: images in the layer list. Select the image to filter.
- "Weight" float: input denoising weight (smaller = smoother).
- "Epsilon" float: input tolerance for stop criterion.
- "Max Iterations" integer: input the max number of iterations allowed for optimization.
- "Isotropic" checkbox: leave checked if noise is isotropic along all axes. Uncheck for anisotropic denoising.
- "Along Axis" checkbox: check to apply the operation along an axis of an image stack.
- "Axis" drop-dpown: select the axis to apply the operation along if "Along Axis" is checked.
- "Filter" button: click to perform the filter operation.

**TV Chambolle Filter**

A widget for applying a total variation Chambolle filter to an image/stack. A TV Chambolle filter attempts to smooth an image while remaining similar
to the original image.
More info: https://scikit-image.org/docs/stable/api/skimage.restoration.html#skimage.restoration.denoise_tv_chambolle
- "Image" drop-down: images in the layer list. Select the image to filter.
- "Weight" float: input denoising weight (greater = smoother).
- "Epsilon" float: input tolerance for stop criterion.
- "Max Iterations" integer: input the max number of iterations allowed for optimization.
- "Along Axis" checkbox: check to apply the operation along an axis of an image stack.
- "Axis" drop-dpown: select the axis to apply the operation along if "Along Axis" is checked.
- "Filter" button: click to perform the filter operation.

**Wavelet Filter**

A widget for applying a wavelet filter to an image/stack. A wavelet filter denoises an image in the wavelet domain (similar to the frequency domain).
More info: https://scikit-image.org/docs/stable/api/skimage.restoration.html#skimage.restoration.denoise_wavelet
- "Image" drop-down: images in the layer list. Select the image to filter.
- "Wavelet" drop-down: select the wavelet to use for wavelet domain conversion.
- "Mode" drop-down: select the type of denoising to be performed.
- "Sigma" float: input the standard deviation of the noise.
- "Wavelet Levels" integer: input the wavelet decomposition level.
- "Threshold Method" drop-down: select the wavelet thresholding method to be used.
- "Rescale Sigma" checkbox: leave checked to rescale the input sigma if the image is rescaled for denoising.
- "Along Axis" checkbox: check to apply the operation along an axis of an image stack.
- "Axis" drop-dpown: select the axis to apply the operation along if "Along Axis" is checked.
- "Filter" button: click to perform the filter operation.

Segmentation Tab
----------------
A tab containing widgets that can segment images and label image segmentations.

**Manual Threshold**

A widget for manual binary segmentation of an image/stack.
- "Image" drop-down: images in the layer list. Select the image to segment.
- "Preview" checkbox: check to turn on a label layer preview of what will be segmented with the current range. Updates dynamically if left on.
- "Range" slidebar: adjust the lower and upper inclusive bounds of the segmentation. Click on the intensity readout above each slider to type in a value.
- "Segment" button: click to perform the segmentation operation.

**Label**

A widget for labeling segmented images/stacks using connectivity or watershed based methods.
More info: https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.label,
https://scikit-image.org/docs/stable/api/skimage.segmentation.html#skimage.segmentation.watershed
- "Image" drop-down: images in the layer list. Select the segmented image to label.
- "Method" drop-down: select the labeling method.
- "Connectivity" drop-down: select the number of orthogonal hops allowed to consider a neighboring pixel connected (applies to both methods).
- "Watershed Radius" integer: if "Method" is "Watershed", input the radius of the watershed kernel (larger = larger watersheds).
- "Watershed Compactness" float: if "Method" is "Watershed", input the compactness factor of the watershed regions (higher = more compact).
- "Background" integer: input the intensity of the background ROI.
- "Along Axis" checkbox: check to apply the operation along an axis of an image stack.
- "Axis" drop-dpown: select the axis to apply the operation along if "Along Axis" is checked.
- "Apply Mask" checkbox: check to apply a mask to the image during labeling. Pixels that are masked will not be labeled.
- "Mask" drop-down: images in the layer list. Select the mask to be applied if "Apply Mask" is checked.
- "Label Segmentation" button: click to perform the labeling operation.

**Histogram Threshold**

A widget for histogram-based segmentation algorithms of images/stacks.
More info: https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_isodata,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_li,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_mean,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_minimum,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_otsu,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_triangle,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_yen
- "Image" drop-down: images in the layer list. Select the image to segment.
- "Method" drop-down: select the algorithm to be used for segmentation.
- "Otsu Classes" integer: if "Method" is "Otsu", input the number of ROIs to segment.
- "Apply Mask" checkbox: check to apply a mask to the image during segmentation. Pixels that are masked will not be included in the histogram.
- "Mask" drop-down: images in the layer list. Select the mask to be applied if "Apply Mask" is checked.
- "Segment" button: click to perform the segmentation operation.

**Local Threshold**

A widget for neighborhood-based segmentation algorithms of images/stacks.
More info: https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_local,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_niblack,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_sauvola,
https://scikit-image.org/docs/stable/api/skimage.filters.rank.html#skimage.filters.rank.threshold
- "Image" drop-down: images in the layer list. Select the image to segment.
- "Method" drop-down: select the algorithm to be used for segmentation.
- "Radius" integer: input the kernel radius.
- "Niblack or Savoula Sigma Weight" float: if "Method" is "Niblack" or "Savoula", input the weight of the standard deviation of intensities.
- "Savoula Sigma Range" float: if "Method" is "Savoula", input the dynamic standard deviation range. Leave as 0 for automatic calculation.
- "Apply Mask" checkbox: check to apply a mask to the image during segmentation. Pixels that are masked will be segmented as background.
- "Mask" drop-down: images in the layer list. Select the mask to be applied if "Apply Mask" is checked.
- "Segment" button" click to perform the segmentation operation.

**Random Walk**

A widget for random walk segmentation of images/stacks.
More info: https://scikit-image.org/docs/stable/api/skimage.segmentation.html#skimage.segmentation.random_walker
- "Image" drop-down: images in the layer list. Select the image to segment.
- "Beta" float: input penalization coefficient for walker model (higher = more difficult diffusion).
- "Lower Percentile" float: input lower intensity percentile for use as random walk marker.
- "Upper Percentile" float: input upper intensity percentile for use as random walk marker.
- "Segment" button: click to perform segmentation operation.

**Morphological Snakes**

A widget for morphological snake segmentation of images/stacks.
More info: https://scikit-image.org/docs/stable/api/skimage.segmentation.html#skimage.segmentation.morphological_chan_vese,
https://scikit-image.org/docs/stable/api/skimage.segmentation.html#skimage.segmentation.morphological_geodesic_active_contour
- "Image" drop-down: images in the layer list. Select the image to segment.
- "Method" drop-down: select the morphological snake method.
- "Iterations" integer: input the number of iterations to run the algorithm for optimization.
- "Square Size" integer: input square size of the initial level set.
- "GAC Alpha" float: if "Method" is "GAC", input inversion steepness for IGG-based edge detection.
- "GAC Sigma" float: if "Method" is "GAC", input standard deviation for IGG-based edge detection.
- "GAC Smoothing" integer: if "Method" is "GAC", input smoothing iterations (larger = smoother segmentation).
- "Segment" button: click to perform segmentation operation.

Morphology Tab
--------------
A tab containing widgets that apply morphology-based filters to segmented images.

**Remove Small Objects**

A widget for removing small particles or holes in segmented images/stacks.
More info: https://scikit-image.org/docs/stable/api/skimage.morphology.html#skimage.morphology.remove_small_objects,
https://scikit-image.org/docs/stable/api/skimage.morphology.html#skimage.morphology.remove_small_holes
- "Image" drop-down: images in the layer list. Select the image to remove objects.
- "Method" drop-down: select "Particles" for small white objects or "Holes" for small black objects.
- "Connectivity" drop-down: select the number of orthogonal hops allowed to consider a neighboring pixel connected (applies to both methods).
- "Size Threshold" float: input the smallest allowed size of the objects being removed.
- "Background" integer: input the background ROI intensity.
- "Pixel Scale" float: input the units/pixel (leave as 1 if "Size Threshold" is entered in pixels).
- "Along Axis" checkbox: check to apply the operation along an axis of an image stack.
- "Axis" drop-dpown: select the axis to apply the operation along if "Along Axis" is checked.
- "Remove Objects" button: click to perform the remove objects operation.

**Dilation**

A widget for dilating segmented images.
More info: https://scikit-image.org/docs/stable/api/skimage.morphology.html#skimage.morphology.dilation
- "Image" drop-down: images in the layer list. Select the image to dilate.
- "Iterations" integer: input the number of dilations to perform.
- "Along Z Axis" checkbox: check to perform erosions along the Z axis if image is 3D.
- "Dilate" button: click to perform the dilation operation.

**Erosion**

A widget for eroding segmented images.
More info: https://scikit-image.org/docs/stable/api/skimage.morphology.html#skimage.morphology.erosion
- "Image" drop-down: images in the layer list. Select the image to erode.
- "Iterations" integer: input the number of erosions to perform.
- "Along Z Axis" checkbox: check to perform erosions along the Z axis if image is 3D.
- "Erode" button: click to perform the erosion operation.

**Closing**

A widget for closing segmented images. Closing is defined as a dilation followed by an erosion and is good for removing small dark spots
(i.e. "closing" dark holes in the image).
- "Image" drop-down: images in the layer list. Select the image to close.
- "Dilations" integer: input the number of dilations to perform before performing erosions.
- "Erosions" integer: input the number of erosions to perform after performing dilations.
- "Along Z Axis" checkbox: check to perform erosions along the Z axis if image is 3D.
- "Close" button: click to perform the closing operation.

**Opening**

A widget for opening segmented images. Opening is defined as an erosion followed by a dilation and is good for removing small bright spots
(i.e. "opening" large dark holes in the image).
- "Image" drop-down: images in the layer list. Select the image to open.
- "Erosions" integer: input the number of erosions to perform before performing dilations.
- "Dilations" integer: input the number of dilations to perform after performing erosions.
- "Along Z Axis" checkbox: check to perform erosions along the Z axis if image is 3D.
- "Open" button: click to perform the opening operation.

**Top Hat**

A widget for performing tophats on images. A black top hat is defined as a closing of an image subtracted by the original image and is good for
returning small dark spots. A white top hat is defined as an image subtracted by its opening and is good for returning small bright spots.
- "Image" drop-down: images in the layer list. Select the image to top hat.
- "Method" drop-down: select the top hat method.
- "Dilations" integer: input the number of dilations to perform in the selected top hat method.
- "Erosions" integer: input the number of erosions to perform in the selected top hat method.
- "Along Z Axis" checkbox: check to perform erosions along the Z axis if image is 3D.
- "Top Hat" button: click to perform the top hat operation.

Features Tab
------------
A tab containing widgets that detect features in images.

**Edge Detection**

A widget for detecting edges in images/stacks.
More info: https://scikit-image.org/docs/stable/api/skimage.feature.html#skimage.feature.canny,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.farid,
https://scikit-image.org/docs/stable/api/skimage.segmentation.html#skimage.segmentation.inverse_gaussian_gradient,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.laplace,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.prewitt,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.roberts,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.scharr,
https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.sobel
- "Image" drop-down: images in the layer list. Select the image to detect edges.
- "Method" drop-down: select the edge-detection method to use.
- "Edges Method" drop-down: select the method for handling pixels on the edge of the image.
- "Canny or IGG Sigma" float: if "Method" is "Canny" or "IGG", input the standard deviation of intensity values.
- "IGG Alpha" float: if "Method" is "IGG", input inversion steepness.
- "Laplace K Size" integer: if "Method" is "Laplace", input the Laplacian operator size.
- "Along Axis" checkbox: check to apply the operation along an axis of an image stack.
- "Axis" drop-dpown: select the axis to apply the operation along if "Along Axis" is checked.
- "Detect Edges" button: click to perform the edge detection operation.

**Corner Detection**

A widget for detecting corners in images/stacks.
More info: https://scikit-image.org/docs/stable/api/skimage.feature.html#skimage.feature.corner_fast,
https://scikit-image.org/docs/stable/api/skimage.feature.html#skimage.feature.corner_harris,
https://scikit-image.org/docs/stable/api/skimage.feature.html#skimage.feature.corner_kitchen_rosenfeld,
https://scikit-image.org/docs/stable/api/skimage.feature.html#skimage.feature.corner_moravec,
https://scikit-image.org/docs/stable/api/skimage.feature.html#skimage.feature.corner_shi_tomasi
- "Image" drop-down: images in the layer list. Select the image to detect corners.
- "Method" drop-down: select the corner detection algorithm.
- "Fast N" integer: if "Method" is "Fast", input the number of consecutive pixels for corner detection.
- "Fast Threshold" float: if "Method" is "Fast", input the threshold for corner validation (smaller = more corners).
- "Harris Method" drop-down: if "Method" is "Harris", select the Harris detection method.
- "Harris K" float: if "Method" is "Harris" and "Harris Method" is "K", input corner from edge sensitivity factor.
- "Harris Epsilon" float: if "Method" is "Harris" and "Harris Method" is "Epsilon", input normalization factor.
- "Harris or Shi Tomasi Sigma" float: if "Method" is "Harris" or "Shi Tomasi", input Gaussian kernel standard deviation.
- "Moravec Window Size" integer: if "Method" is "Moravec", input the kernel window size.
- "Correct Anomalies" checkbox: leave checked to remove corners that appear extraneously in the middle of open regions in the original image.
- "Return Mode" drop-down: select the ouput mode for corner analysis.
- "Detect Corners" button: click to perform the coner detection operation.

**Skeleton Detection**

A widget for detecting the skeleton of segmented features in an image/stack.
More info: https://scikit-image.org/docs/stable/api/skimage.morphology.html#skimage.morphology.skeletonize
- "Image" drop-down: images in the layer list. Select the image to skeletonize.
- "Method" drop-down: select the skeleton detection algorithm.
- "Detect Skeleton" button: perform the skeleton detection operation.

Analysis Tab
------------
A tab containing widgets that generate plots and measurements of images.

**Histogram**

A widget for generating a gray-level histogram of an image/stack. Histogram statistics are displayed in the terminal upon generation.
More info: https://scikit-image.org/docs/stable/api/skimage.exposure.html#skimage.exposure.histogram
- "Image" drop-down: images in the layer list. Select the image to generate a histogram.
- "Normalize" checkbox: check to normalize the counts of the histogram. Y axis will read "Probability Density" instead of "Counts".
- "Add CDF" checkbox: check to add a cumulative distribution function curve plotted on the right Y axis.
- "Remove Edges" checkbox: check to remove the highest and lowest values of the histogram in case of anomalous extreme values.
- "X Min" float: input the minimum X value to plot.
- "X Max" float: input the maximum X value to plot.
- "Y Max" float: input the maximum Y value.
- "Num Bins" integer: input the number of bins for the histogram.
- "Apply Mask" checkbox: check to apply a mask during histogram generation. Pixels that are masked will not be included.
- "Mask" drop-down: images in the layer list. Select the mask to be applied if "Apply Mask" is checked.
- "Add as Parameter" checkbox: check to add the histogram generation step to the parameters log.
- "Plot Histogram" button: click to plot the histogram.

**Line Scan**

A widget for generating an intensity profile along a drawn line.
- "Image" drop-down: images in the layer list. Select the image to line scan.
- "Shapes" drop-down: shape layers in the layer list. Select the shapes layer with the drawn line.
- "Plot Line Scan" button: click to plot the line scan.

**Gray Level**

A widget for generating gray level statistical plots along each axis of a 3D image stack.
- "Image" drop-down: images in the layer list. Select the image to plot gray levels.
- "Apply Mask" checkbox: check to apply a mask during gray level plotting. Masked pixels will not be included.
- "Mask" drop-down: images in the layer list. Select the mask to be applied if "Apply Mask" is checked.
- "Add as Parameter" checkbox: check to add the gray level plot step to the parameters log.
- "Plot Gray Level" button: click to plot the gray level statistics.

**FFT**

A widget for computing a fast-Fourier transform of an image/stack.
More info: https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft2.html#scipy.fft.fft2,
https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fftn.html#scipy.fft.fftn
- "Image" drop-down: images in the layer list. Select the image to compute an FFT.
- "Along Z Axis" checkbox: check to perform the FFT along the Z axis of a 3D image stack.
- "FFT" button: click to perform the FFT operation.

**Misc Calculations**

A widget for calculating miscellaneous information about an image/stack such as gray level statistics, intensity volume percentages (as used in saturation), intensity volume/area, segmented phase surface area/perimeter, and segmented phases contact area/perimeter. Calculated values are displayed in the terminal upon generation.
- "Image" drop-down: images in the layer list. Select the image to calculate information.
- "Method" drop-down: select the calculation to be performed.
- "Min Percent" float: if "Method" is "Percent Intensities", input the minimum percentage to calculate.
- "Max Percent" float: if "Method" is "Percent Intensities", input the maximum percentage to calculate.
- "Include Background" checkbox: if "Method" is "Volume/Area", check to include the volume/area of the background phase in the     case of a segmented image/stack.
- "Surface Phase" float: if "Method" is "Surface Area/Perimeter", input the intensity of the phase to calculate surface area/      perimeter.
- "Contact Phase 1" float: if "Method" is "Contact Area/Perimeter", input the intensity of one of the phases.
- "Contact Phase 2" float: if "Method" is "Contact Area/Perimeter", input the intensity of the other phase.
- "Pixel Scale" float: if "Method" is "Volume/Area", "Surface Area/Perimeter", or "Contact Area/Perimeter", input the unit         length per pixel.
- "Units" string: if "Method" is "Volume/Area", "Surface Area/Perimeter", or "Contact Area/Perimeter", input the length units.
- "Apply Mask" checkbox: check to apply a mask during calculation. Masked pixels will not be included in calculations.
- "Mask" drop-down: images in the layer list. Select the mask to be applied if "Apply Mask" is checked.
- "Add as Parameter" checkbox: check to include the miscellaneous calculation step in the parameters log to be output during       batch processing.
- "Calculate" button: click to perform the calculation operation.

**Axial Distributions**

A widget for generating a plot of measured volume or area of of a segmented phase along a specified axis for a 3D image stack.
- "Image" drop-down: images in the layer list. Select the image to plot an axial distribution.
- "Type" drop-down: select whether area or volume is being calculated along the specified axis.
- "Axis" drop-down: select the axis along which the plot is generated.
- "Domain Size" checkbox: check to calculate domain area/volume distributions along the axis instead of total area/volume. NOTE,   this feature does not currently work and will return an error.
- "Domain Size Connectivity" drop-down: if "Domain Size" is checked, select the number of orthogonal hops allowed to consider a    neighboring pixel connected.
- "Include Background" checkbox: check to plot the area/volume of the background phase in addition to the segmented phases.
- "Background" float: input the background phase intensity.
- "Pixel Scale" float: input the unit length per pixel.
- "Pixel Units" string: input the length units.
- "Normalize" checkbox: check to normalize the plotted area/volume to plot probability density instead.
- "Remove Edges" checkbox: check to remove the end values in the case of anomalous extremes.
- "X Min" float: input the minimum X value to plot.
- "X Max" float: input the maximum X value to plot.
- "Y Max": float: input the maximum Y value.
- "Time Series" checkbox: check if the axis being plotted along is a temporal axis rather than a spatial axis.
- "Time Units" string: if "Time Series" is checked, input the temporal axis units.
- "Time Scale" float: if "Time Series" is checked, input the temporal length per slice.
- "Apply Mask" checkbox: check to apply a mask during calculation. Masked pixels will not be included in calculations.
- "Mask" drop-down: images in the layer list. Select the mask to be applied if "Apply Mask" is checked.
- "Add as Parameter" checkbox: check to add the axial distribution plot generation to the parameters log.
- "Plot Distribution" button: click to generate the axial distribution plot.

**Domain Size Distribution**

A widget for generating a domain size distribution plot for a segmented image/stack. If the image is not already labeled (see the label widget in the Segmentation tab), it will be labeled with the connectivity method.
- "Image" drop-down: images in the layer list. Select the image to plot a segmented domain size distribution.
- "Type" drop-down: select the format to calculate domain size. Volume and area are the total measured volume/area for each        domain while diameter and radius initially calculate the area/volume and then calculate the diameter/radius assuming a           circular or spherical domain shape.
- "Connectivity" drop-down: if the image is not labeled, select the number of orthogonal hops allowed to consider a                neighboring pixel connected.
- "Background" float: input the background intensity.
- "Pixel Scale" float: input the unit length per pixel.
- "Units" string: input the length units.
- "Normalize" checkbox: check to normalize the domain size counts to plot probability density instead.
- "Remove Edges" checkbox: check to exclude the end domain sizes in the case of anomalous extremes.
- "X Min" float: input the minimum X value to plot.
- "X Max" float: input the maximum X value to plot.
- "Y Max": float: input the maximum Y value.
- "Num Bins" integer: input the number of bins for the domain size distribution.
- "Max Bound" float: input the maximum bound to include in the bin generation. Leave as "0" to use the maximum measured value.
- "Apply Mask" checkbox: check to apply a mask during calculation. Masked pixels will not be included in calculations.
- "Mask" drop-down: images in the layer list. Select the mask to be applied if "Apply Mask" is checked.
- "Add as Parameter" checkbox: check to add the domain size distribution plot generation to the parameters log.
- "Plot Distribution" button: click to generate the domain size distribution plot.

**Heat Maps**

A widget to generate a thickness or positional heat map along an axis from a segmented 3D image stack.
- "Image" drop-down: images in the layer list. Select the image stack to plot a heat map.
- "Axis" drop-down: select the axis along which the heat mapped value should be calculated.
- "Method" drop-down: select "Thickness" to measure the thickness of a segmented phase along the specified axis or "Height" to     measure the distance to the closest or farthest pixel belonging to the segmented phase along the specified axis.
- "Heat Direction" drop-down: if "Method" is "Height", select "Near" to plot the closest (lowest index) or "Far" to plot the       farthest (highest index) pixel belonging to the segmented phase along the specified axis.
- "Color Map" drop-down: select the color map to use for the heat map.
- "Pixel Scale" float: input the unit length per pixel.
- "Units" string: input the length units.
- "Define Limits" checkbox: check to define the thickness/height limits for the heat map. Leave unchecked to use the smallest      and largest values measured in the heat map calculation.
- "Min Value" float: if "Define Limits" is checked, input the minimum heat mapped value.
- "Max Value" float: if "Define Limits" is checked, input the maximum haet mapped value.
- "Alternate Colorbar Label" checkbox: check to input a different label for the colorbar than "Thickness" or "Height"
- "Colorbar Label" string: if "Alternate Colorbar Label" is checked, input the alternate colorbar label.
- "Apply Mask" checkbox: check to apply a mask during calculation. Masked pixels will not be included in calculations.
- "Mask" drop-down: images in the layer list. Select the mask to be applied if "Apply Mask" is checked.
- "Return Array" checkbox: check to return the generated heat map array as an image in the layers list for processing.
- "Add as Parameter" checkbox: check to add the heat map generation step to the parameters log.
- "Plot Heat Map" button: click to generate the heat map.

------------
