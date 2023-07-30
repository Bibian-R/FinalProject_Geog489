***  -*- AccessMod 5 Data Creator Description -*-  ***
The app created as part of Geog 489 Final project facilitates geospatial data processing, enabling users to select vector and raster files, perform clipping and
projection, and save output files. Its primary purpose is to prepare data required for modeling geographical
accessibility to points, such as health facilities, using AccessMod 5 software. This is achieved by selecting an
administrative unit as the basis for analysis. The datasets include:

*Health facilities
*River
*Road
*Water body e.g.. lakes
*Protected Areas e.g forest
*Elevation
*Population
*Land use\Land Cover

###############The following directory are associated with the app #####################################################
1. GUi directory : contains all .ui files saved from QT designer
    *. mainApp_gui.ui
    *. saveFile_gui.ui
2. Images directory: contains all images
3. Input Data: all input raster and vector data files for Kenya that are prerequisite to modelling access in AccessMod
    *. Vector Data: all shapefiles
    *. Raster Data: all raster files
    *. Admin Boundary: Administrative units that serve as Clip Feature
4.Output: Store all outputs from the App. Kilifi County along the coast of Kenya has been used as example
5.Scripts directory: contains all .py file that run the app. They include:
    *. main_script.py: this is the main script that runs the app and contains additional custom classes defined
       in separate files
    *. access_mod_dataprep.py: contains all the custom class/methods for geoprocessing (select, clipping, reproject and save)
       raster and vector data. The classes are derived from the arcpy module
    ##### Gui Files#####
The GUI files were created in QT designer and compiled into .py files. They include:
    *. main_app_gui.py : This is the mainwindow for the AccessMod 5 Data Creator Application
    *. save_file_gui.py : This is GUI for the save feature dialog window