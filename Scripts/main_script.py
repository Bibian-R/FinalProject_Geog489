# -*- Main script running the AccessMod Data Prep Creator App -*-
# -*- By: Bibian Robert -*-
# -*- GEOG 489: Final Project -*-
# ***** Script Description ******
# 1. class saveFileGUI(QDialog) - a class derived from QDialog class which opens a dialog window for saving files
# It is using Qt for Python (PyQt) to create the graphical user interface (GUI) elements.
# 2. class MainAppGui(QMainWindow)- a class of the main application window derived from QMainWindow.
# the app does geospatial data processing and provides functionality to select vector and raster files, perform clipping
# and projection, and save output files. This class is built using PyQt for the GUI elements, and it relies on other
# custom classes or modules such as access_mod_dataprep, VectorProjectAndClip, and RasterClipAndProject

# import general modules---
import traceback
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog, QListWidgetItem, QStyle
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys
import arcpy
import os

# import GUI modules..
import main_app_gui
import save_file_gui

# import custom classes/modules---
import access_mod_dataprep
from access_mod_dataprep import VectorProjectAndClip, RasterClipAndProject


# This class derived from QDialog opens a dialog window for saving files-----------------------------------------------
class SaveFileGui(QDialog):
    def __init__(self):
        super(SaveFileGui, self).__init__()
        self.ui = save_file_gui.Ui_Dialog()
        self.ui.setupUi(self)

        #  connect signals
        self.ui.newOutputFileBrowseTB.clicked.connect(self.saveNewFile)

    #  method that opens dialog when tool button(newOutputFileBrowseTB) is clicked to save new files---
    def saveNewFile(self):
        filter_options = "GeoTIFF (*.tif);;PNG (*.png);;JPEG (*.jpg);;Geopackage (*.gpkg);;Shapefile (*.shp);;All " \
                         "Files (*)"
        file, _ = QFileDialog.getSaveFileName(self, 'Save File as', "", filter_options)
        if file:
            self.ui.newOutputFileLE.setText(file)
        #


# This class derived from QMainWindow is the main application window for the app and runs vector and raster data
# geoprocessing clipping, projection and saving----------------------------------------
class MainAppGui(QMainWindow):
    def __init__(self, parent=None):
        super(MainAppGui, self).__init__(parent)
        print("Initializing MainAppGui...")  # check app is running
        self.ui = main_app_gui.Ui_MainWindow()
        self.ui.setupUi(self)

        # ---------------------------------Connect signals to slots-----------------------------------------------------
        # Vector input files---
        self.ui.healthFacilBrowseTB.clicked.connect(lambda: self.selectVectorFile(self.ui.healthFacilLE))
        self.ui.roadFileBrowseTB.clicked.connect(lambda: self.selectVectorFile(self.ui.roadFileLE))
        self.ui.riverBrowseTB.clicked.connect(lambda: self.selectVectorFile(self.ui.riverLE))
        self.ui.waterbodyBrowseTB.clicked.connect(lambda: self.selectVectorFile(self.ui.waterbodyLE))
        self.ui.protectedAreaBrowseTB.clicked.connect(lambda: self.selectVectorFile(self.ui.protectedAreaLE))

        # Raster data input files---
        self.ui.landuseBrowseTB.clicked.connect(lambda: self.selectRasterFile(self.ui.landuseLE))
        self.ui.elevationBrowseTB.clicked.connect(lambda: self.selectRasterFile(self.ui.elevationLE))
        self.ui.populationBrowseTB.clicked.connect(lambda: self.selectRasterFile(self.ui.populationFileLE))

        #  Save Vector files---
        self.ui.saveRoadsTB.clicked.connect(lambda: self.selectSaveVector(self.ui.saveRoadLE))
        self.ui.saveRoadPB.clicked.connect(lambda: self.createNewFeature(self.ui.saveRoadLE))
        self.ui.saveHealthFacilBrowseTB.clicked.connect(lambda: self.selectSaveVector(self.ui.saveHealthFacilLE))
        self.ui.saveHealthFacilPB.clicked.connect(lambda: self.createNewFeature(self.ui.saveHealthFacilLE))
        self.ui.saveRiverTB.clicked.connect(lambda: self.selectSaveVector(self.ui.saveRiverLE))
        self.ui.saveRiverPB.clicked.connect(lambda: self.createNewFeature(self.ui.saveRiverLE))
        self.ui.saveWaterbodyTB.clicked.connect(lambda: self.selectSaveVector(self.ui.saveWaterbodyLE))
        self.ui.saveWaterbodyPB.clicked.connect(lambda: self.createNewFeature(self.ui.saveWaterbodyLE))
        self.ui.saveProtectedAreaTB.clicked.connect(lambda: self.selectSaveVector(self.ui.saveProtectAreaLE))
        self.ui.saveProtectAreaPB.clicked.connect(lambda: self.createNewFeature(self.ui.saveProtectAreaLE))

        #  Save raster files---
        self.ui.popSaveBrowseTB.clicked.connect(lambda: self.selectSaveRaster(self.ui.popSaveLE))
        self.ui.savePopPB.clicked.connect(lambda: self.createNewFeature(self.ui.popSaveLE))
        self.ui.landuseSaveBrowseTB.clicked.connect(lambda: self.selectSaveRaster(self.ui.landuseSaveLE))
        self.ui.saveLandusePB.clicked.connect(lambda: self.createNewFeature(self.ui.landuseSaveLE))
        self.ui.elevationSaveBrowseTB.clicked.connect(lambda: self.selectSaveRaster(self.ui.elevationSaveLE))
        self.ui.saveElevationPB.clicked.connect(lambda: self.createNewFeature(self.ui.elevationSaveLE))

        # Select clip file---
        self.ui.clipFtBrowseTB.clicked.connect(self.selectClipFile)
        # Update Combo Box (updateListFieldNameCB) with field names form selected clip file---
        self.ui.inputClipFtLE.editingFinished.connect(self.updateListFieldNameCB)
        # Update Combo Box (selectFieldNameCB) with field items from the selected field Name---
        self.ui.selectFieldNameCB.currentIndexChanged.connect(self.updateSelectFieldItems)

        # Display projected spatial reference system on updateSelectPrjCB after Radio Button is clicked---
        self.ui.selectPrjRB.clicked.connect(self.updateSelectPrjCB)

        # run reproject and Clip---
        self.ui.runReprojectClipPB.clicked.connect(self.runClipAndReproject)

        # confirm all new saved files are created and projected---
        self.ui.confirmCrsPB.clicked.connect(self.populateListView)

        # set exit icon---
        self.ui.actionExit.setIcon(app.style().standardIcon(QStyle.SP_DialogCancelButton))

        # self.ui.runReprojectClipPB.clicked.connect(self.displaySpatialRef)

    def selectVectorFile(self, lineedit):
        """opens a dialog box that allows user to select vector files"""

        # fileOptions = "Geopackage (*.gpkg);;Shapefile (*.shp);;All Files (*)"  # other file formats
        file, _ = QFileDialog.getOpenFileName(self, 'Select Vector File', "*.shp")
        if file:
            lineedit.setText(file)

    def selectRasterFile(self, lineedit):
        """opens a dialog box that allows user to select raster files"""

        # fileOptions = "GeoTIFF (*.tif);;PNG (*.png);;JPEG (*.jpg);;All Files (*)"  # other file formats
        file, _ = QFileDialog.getOpenFileName(self, 'Select Raster File', "*.tif")
        if file:
            lineedit.setText(file)

    def selectClipFile(self):
        """opens a dialog box that allows user to select Clip feature"""
        file, _ = QFileDialog.getOpenFileName(self, 'Select Vector File', "*.shp")
        if file:
            self.ui.inputClipFtLE.setText(file)
            self.updateListFieldNameCB()

    def updateListFieldNameCB(self):
        """update selectFieldNameCB combo box with field Names from the selected clip feature"""

        clipFeature = self.ui.inputClipFtLE.text()
        accessObj = access_mod_dataprep.AccessModDataPrep()  # create an instance of the AccessModDataPrep() class
        try:
            fieldNames = accessObj.getValidFieldsForShapefile(clipFeature)  # call getValidFieldsForShapefile method
            # print("Field Names:", fieldNames)
            self.ui.selectFieldNameCB.clear()  # clear previous selection
            self.ui.selectFieldNameCB.addItems(fieldNames)
            self.updateSelectFieldItems()
        except Exception as e:
            print("Error:", e)
            # Clear the combo box if there was an error
            self.ui.listFieldNameCB.clear()

    def updateSelectFieldItems(self):
        """update targetClipFtCB combo box with field items from the selected field Name"""

        selectedField = self.ui.selectFieldNameCB.currentText()
        fileName = self.ui.inputClipFtLE.text()
        accessObj = access_mod_dataprep.AccessModDataPrep()  # create an instance of the AccessModDataPrep() class
        self.ui.targetClipFtCB.clear()  # clear previous selection
        items = accessObj.listFieldItems(fileName, selectedField)  # calls the listField Items method
        self.ui.targetClipFtCB.addItems(items)  # add items of the selected field Name

    def displaySpatialRef(self):
        """used to display spatial reference system for selected feature"""
        inputFeature = self.ui.inputClipFtLE.text()
        accessObj = access_mod_dataprep.AccessModDataPrep()  # Create an instance of AccessModDataPrep class
        accessObj.checkSpatialRef(inputFeature)  # call the checkSpatialRef methods

    def createNewFeature(self, newFtLineEdit):
        """Opens a dialog box to create new  feature"""
        dialog = SaveFileGui()  # Create an instance of SaveFileGui dialog
        if dialog.exec_() == QDialog.Accepted:  # Check if the dialog was accepted
            file = dialog.ui.newOutputFileLE.text()
            try:
                newFtLineEdit.setText(file)
                self.ui.statusbar.showMessage("New Feature has been created.")
            except Exception as e:
                self.ui.QMessageBox.information(self, 'Operation failed',
                                                'Creating new output shapefile failed with ' + str(
                                                    e.__class__) + ': ' + str(e),
                                                self.ui.QMessageBox.Ok)
                self.ui.statusbar.clearMessage()

    def selectSaveVector(self, saveVectorLE):
        """Opens a dialog box to select save vector files"""
        # filter_options = "GeoTIFF (*.tif);;PNG (*.png);;JPEG (*.jpg);;Geopackage (*.gpkg);;Shapefile (*.shp);;All " \
        # "Files (*)"  # other file formats
        file, _ = QFileDialog.getOpenFileName(self, 'Select Vector File', "*.shp")
        if file:
            saveVectorLE.setText(file)
    def selectSaveRaster(self, saveRasterLE):
        """Opens a dialog box to select save raster files"""
        # filter_options = "GeoTIFF (*.tif);;PNG (*.png);;JPEG (*.jpg);;Geopackage (*.gpkg);;Shapefile (*.shp);;All " \
        # "Files (*)"  # other file formats
        file, _ = QFileDialog.getOpenFileName(self, 'Select Raster File', "*.tif")
        if file:
            saveRasterLE.setText(file)

    def updateSelectPrjCB(self):
        """update selectPrj combo box with UTM spatial reference names"""

        accessObj = access_mod_dataprep.AccessModDataPrep()
        srsList = accessObj.listSpatialRef()
        self.ui.selectPrjCB.clear()
        if self.ui.selectPrjRB.isChecked():
            self.ui.selectPrjCB.addItems(srsList)

    def populateListView(self):
        """Populates list View with the projected spatial reference system of the clipped and saved features"""

        print("running...")  # test to see if method is being called
        self.ui.listPrjLW.clear()  # Clear the current items in the list view
        try:
            # Retrieve the text from each line edit and add it to the list view
            lineEditList = [
                # vector
                self.ui.saveRoadLE,
                self.ui.saveRiverLE,
                self.ui.saveProtectAreaLE,
                self.ui.saveHealthFacilLE,
                self.ui.saveWaterbodyLE,
                # raster
                self.ui.popSaveLE,
                self.ui.landuseSaveLE,
                self.ui.elevationSaveLE

                # Add more line edits as needed
            ]
            accessObj = access_mod_dataprep.AccessModDataPrep()  # create an instance of AccessModDataPrep class
            # loop through each item in the Line Edit list and extract the file
            for lineEdit in lineEditList:
                text = lineEdit.text()
                if text:
                    srf = accessObj.checkSpatialRef(text)  # call the checkSpatialRef method
                    item = QListWidgetItem(srf)
                    self.ui.listPrjLW.addItem(item)  # populate the list View widget spatial reference for each file

        except Exception as e:
            print("Error in populateListView:", e)
            traceback.print_exc()  # Print the traceback for debugging

    def runClipAndReproject(self):
        """this method clips and reprojects vector and raster data based on user inputs"""
        try:
            # create a list of all input features both vector and raster
            inputFeatures = [self.ui.healthFacilLE.text(), self.ui.roadFileLE.text(), self.ui.riverLE.text(),
                             self.ui.waterbodyLE.text(), self.ui.protectedAreaLE.text(),
                             self.ui.populationFileLE.text(),
                             self.ui.landuseLE.text(), self.ui.elevationLE.text()]
            # create a list of all output features both vector and raster
            outputClipFeatures = [self.ui.saveHealthFacilLE.text(), self.ui.saveRoadLE.text(),
                                  self.ui.saveRiverLE.text(), self.ui.saveWaterbodyLE.text(),
                                  self.ui.saveProtectAreaLE.text(), self.ui.popSaveLE.text(),
                                  self.ui.landuseSaveLE.text(), self.ui.elevationSaveLE.text()]
            # print(outputClipFeatures)  # just a check

            clipFeature = self.ui.inputClipFtLE.text()  # access the clip Feature file & store in clipFeature variable

            # Check if the number of user inputs matches user outputs
            if len(inputFeatures) != len(outputClipFeatures):
                print("Error: Number of Vector input files and output names should be the same.")
                return

            targetCountyName = self.ui.targetClipFtCB.currentText()  # access selected target county name
            targetCountyNameField = self.ui.selectFieldNameCB.currentText()  # access selected target county name field
            Crs = self.ui.selectPrjCB.currentText()  # access selected spatial reference system
            outputCrs = arcpy.SpatialReference(Crs)  # create a spatialReference object using Crs as parameter
            # print(outputCrs)  # for check

            # Create an instance of the VectorProjectAndClip class for vector data
            projectClipObjV = VectorProjectAndClip()
            # Create an instance of the RasterProjectAndClip class for Raster data
            projectClipObjR = RasterClipAndProject()

            # Create an instance of the AccessModDataPrep class
            accessObj = access_mod_dataprep.AccessModDataPrep()
            # call the selectTargetAdmin method to select the target Clip Feature
            targetCounty = accessObj.selectTargetAdmin(clipFeature, targetCountyNameField, targetCountyName)

            # Loop through the clipped features and output files and perform clipping and projection
            for inputFeature, outputClipFeature in zip(inputFeatures, outputClipFeatures):
                # !!!!! this section was trying to explore the use of Describe to identify data types but failed to work
                # desc = arcpy.Describe(os.path(inputFeature)[1])
                # if desc.dataType == "Shapefile":
                #     print("The dataset is Shapefile")
                #
                #     # Call the clipFeature method to clip the input feature
                #     projectClipObjV.handleVecProjectAndClip(inputFeature, outputClipFeature, outputCrs, targetCounty)
                # elif desc.dataType == "RasterDataset":
                #     print("The dataset is a raster")
                #
                #     projectClipObjR.handleRasProjectAndClip(inputFeature, outputClipFeature, outputCrs, targetCounty)
                #
                # else:
                #     print("The dataset is neither raster nor shapefile")

                # use of file extension to identify vector files and raster files and applying the appropriate clip and
                # project method----------------------------------------------------------------------------------------

                fileExtension = os.path.splitext(inputFeature)[1].lower()
                if fileExtension == ".shp":  # checks if file is a shapefile and assigns appropriate method
                    fileName = os.path.basename(inputFeature)
                    self.ui.statusbar.showMessage("The dataset {0} is Shapefile".format(fileName))

                    # Call the clipFeature method to clip the input feature
                    projectClipObjV.handleVecProjectAndClip(inputFeature, outputClipFeature, outputCrs, targetCounty)
                elif fileExtension == ".tif":  # checks if file is a raster and assigns appropriate method
                    fileName = os.path.basename(inputFeature)
                    self.ui.statusbar.showMessage("The dataset {0} is Raster".format(fileName))

                    projectClipObjR.handleRasProjectAndClip(inputFeature, outputClipFeature, outputCrs, targetCounty)
                    self.ui.statusbar.showMessage("Reproject and clipping of all files is complete")
                else:
                    fileName = os.path.basename(inputFeature)
                    self.ui.statusbar.showMessage("The dataset {0} is neither raster nor shapefile".format(fileName))
                    #print("The dataset is neither raster nor shapefile")

        except Exception as e:
            # Print the error message and traceback to identify the issue
            print("Error occurred during clipping and projection:", e)
            traceback.print_exc()
            self.ui.QMessageBox.information(self, 'Operation failed',
                                            'Clipping and Reprojecting files failed! ' + str(
                                                e.__class__) + ': ' + str(e),
                                            self.ui.QMessageBox.Ok)
            self.ui.statusbar.clearMessage()


# Create and run the AccessMod 5 Data Prep graphical user interface-----------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainAppGui()
    form.show()
    app.exec_()
