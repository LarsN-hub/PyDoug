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

**Installation**
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
- "Import File": click to import the file.

**Import File Sequence**
A widget for importing sequences of files contained in a folder.
- "Directory Path": click "Choose directory" to open a directory selector dialog to locate the folder containing the images.
- "Import File Sequence": click to import the file sequence.

**Export Image(s)**
A wiget for exporting images (2D or 3D).
- "Image" drop-down: Images in the layer list. Select the image to export.
- "Method" drop-down: Available export formats (tiff or hdf5)
- "Multi Page" checkbox: Leave checked if "Method" is "Tiff" to export as multi-page (3D) tiff. Otherwise exports as tiff sequence.
  Has no functionality if "Method" is "HDF5".
- "Save Folder": click "Choose directory" to open a directory selector dialog to locate the save folder. Note that a folder will
  be created in this folder if exporting as a tiff sequence.
- "Save Name": type in a name for the exported image(s). This will be the name of the folder if exporting as a tiff sequence.
- "Export Image(s)": click to export the image(s).

**Export Parameters**
A widget for exporting the current parameters log.
- "Save Folder": click "Choose directory" to open a directory selector dialog to locate the save folder. Note that a folder will
  be created in this folder with the name provided in "Folder Name".
- "Folder Name": type in a name for the parameters folder.
- "Compress Masks" checkbox: leave checked to convert any masks used to 2D slices of their original 3D volume (if processing 3D images).
  If a mask has the same shape throughout every slice, this can save on storage space. If a mask has a unique shape on different slices,
  DO NOT leave this checked.
- "Export Parameters": click to export the parameters.

**Batch Processing**
A widget for batch processing other image(s) with an exported parameters log (parameters must be exported and saved already).
- "Image Format" drop-down: select "Stacks" if importing image sequences, otherwise select "Singles" for 2D images or multi-page (3D) tiffs.
- "Stack Format" drop-down: if "Image Format" is "Stacks", select "Multi-Page" if stacks are multi-page (3D) tiffs or hdf5-type files.
  Otherwise, select "Sequence" to import folders containing image sequences.
- "Export Images" checkbox: leave checked to export the images after processing. Uncheck if you are just creating plots from the images.
- "Export Multi Page" checkbox: leave checked to export stacks as multi-page (3D) tiffs. Uncheck to export stacks as image sequences.
- "Copy Parameters" checkbox: leave checked to put a copy of the parameters used in the export folder.
- "Run Batch Script": click to open the images selection dialog, followed by the parameters selection dialog, followed by the export
  selection dialog, followed by the batch script itself.

Manipulate Tab
--------------
A tab containing widgets that modify the dimensions of images.

**Trim / Pad**


**Crop**


**Split**


**Join**


**Extend**


Transform Tab
-------------
A tab containing widgets that perform geometric/matrix transformations on images.

**Reslice**


**Rotate**


**Mirror**


**Rescale**


Masking Tab
-----------
A tab containing widgets that can create and apply masks to images.

**Mask**


**Add Shape**


**Create Mask from Shapes**


**Paint**


**Create Mask from Paint**


**Mask Logic Operations**


Pixel Values Tab
----------------
A tab containing widgets that alter the bit-dpeth and intensity values of pixels.

**Convert Type**


**Normalize**


**Saturate**


**Equalize Histogram**


**Invert**


**Re-Assign Intensities**


**RGB to Grayscale**


Denoising Tab
-------------
A tab containing widgets that apply denoising filters to images.

**Bilateral Filter**


**Gaussian Blur**


**Non-Local Means Filter**


**Remove Background**


**Ring Removal**


**TV Bregman Filter**


**TV Chambolle Filter**


**Wavelet Filter**


Segmentation Tab
----------------
A tab containing widgets that can segment images and label image segmentations.

**Manual Threshold**


**Label**


**Histogram Threshold**


**Local Threshold**


**Random Walk**


**Morphological Snakes**


Morphology Tab
--------------
A tab containing widgets that apply morphology-based filters to segmented images.

**Remove Small Objects**


**Dilation**


**Erosion**


**Closing**


**Opening**


**Top Hat**


Features Tab
------------
A tab containing widgets that detect features in images.

**Edge Detection**


**Corner Detection**


**Measure Angles**


Analysis Tab
------------
A tab containing widgets that generate plots and measurements of images.

**Histogram**


**Line Scan**


**Gray Level**


**FFT**


**Misc Calculations**


**Axial Distributions**


**Domain Size Distribution**


**Heat Maps**


------------
