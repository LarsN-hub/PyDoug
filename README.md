-----------
--Preface--
-----------

I am not a software developer. I am a PhD candidate who knows some things about image processing
and wanted to make a GUI-operated resource for people who may not have access to MATLAB or ORS Dragonfly
due to monetary or licensing limitations. Please be patient with me as I navigate through the world
of coding and GitHub best practices, licensing, and all that jazz.

I have only ever used Windows systems, so I cannot say whether or not this works on Linux or Apple
systems nor can I currently provide support for installing this on those systems.

I am working on figuring out how to make this a single, downloadable executable file, but this has
proven more difficult than I realized. Until then, installing PyDoug will require a little bit of work
as explained below.

----------------
--Installation--
----------------

Windows
1. Ensure that Python v3.13 is installed on your computer.
2. Test that you have it by opening Windows PowerShell and typing "python".
   - If it worked, some information about python (3.13._) should pop up and the input line should have
     ">>>" in front of it.
   - If this is the case, type quit() to exit python and proceed. If this did not
     happen, do not continue with this process and figure this out first.
3. Navigate to the Tags section in releases as I am frequently fixing bugs during the alpha phase.
4. Download the zip file for the most recent tag.
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

