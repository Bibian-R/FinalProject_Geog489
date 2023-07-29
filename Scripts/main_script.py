# -*- coding: utf-8 -*-
import traceback

from PyQt5 import QtWidgets
# Form implementation generated from reading ui file 'gui_mainApp.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog, QListWidgetItem, QStyle
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys
import arcpy
import os
# import gui_mainApp_test
import access_mod_dataprep
from access_mod_dataprep import VectorProjectAndClip, RasterClipAndProject
import main_app_gui
import save_file_gui


# from PyQt5 import QtCore, QtGui, QtWidgets

# save Window
class SaveFileGui(QDialog):
    def __init__(self):
        super(SaveFileGui, self).__init__()
        self.ui = save_file_gui.Ui_Dialog()
        self.ui.setupUi(self)

        #  connect signals
        self.ui.newOutputFileBrowseTB.clicked.connect(self.saveNewFile)

        #  opens dialog when tool button is clicked to save new files

    def saveNewFile(self):
        filter_options = "GeoTIFF (*.tif);;PNG (*.png);;JPEG (*.jpg);;Geopackage (*.gpkg);;Shapefile (*.shp);;All " \
                         "Files (*)"
        file, _ = QFileDialog.getSaveFileName(self, 'Save File as', "", filter_options)
        if file:
            self.ui.newOutputFileLE.setText(file)
        #


class MainAppGui(QMainWindow):
    def __init__(self, parent=None):
        super(MainAppGui, self).__init__(parent)
        print("Initializing MainAppGui...")
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

        self.ui.clipFtBrowseTB.clicked.connect(self.selectClipFile)
        self.ui.inputClipFtLE.editingFinished.connect(self.updateListFieldNameCB)
        self.ui.selectFieldNameCB.currentIndexChanged.connect(self.updateSelectFieldItems)
        self.ui.runReprojectClipPB.clicked.connect(self.displaySpatialRef)
        #  Save Vector files---
        self.ui.saveRoadsTB.clicked.connect(lambda: self.openSavedFeature(self.ui.saveRoadLE))
        self.ui.saveRoadPB.clicked.connect(lambda: self.createNewFeature(self.ui.saveRoadLE))
        self.ui.saveHealthFacilBrowseTB.clicked.connect(lambda: self.openSavedFeature(self.ui.saveHealthFacilLE))
        self.ui.saveHealthFacilPB.clicked.connect(lambda: self.createNewFeature(self.ui.saveHealthFacilLE))
        self.ui.saveRiverTB.clicked.connect(lambda: self.openSavedFeature(self.ui.saveRiverLE))
        self.ui.saveRiverPB.clicked.connect(lambda: self.createNewFeature(self.ui.saveRiverLE))
        self.ui.saveWaterbodyTB.clicked.connect(lambda: self.openSavedFeature(self.ui.saveWaterbodyLE))
        self.ui.saveWaterbodyPB.clicked.connect(lambda: self.createNewFeature(self.ui.saveWaterbodyLE))
        self.ui.saveProtectedAreaTB.clicked.connect(lambda: self.createNewFeature(self.ui.saveProtectAreaLE))
        self.ui.saveProtectAreaPB.clicked.connect(lambda: self.createNewFeature(self.ui.saveProtectAreaLE))

        #  Save raster files---

        self.ui.popSaveBrowseTB.clicked.connect(lambda: self.createNewFeature(self.ui.popSaveLE))
        self.ui.savePopPB.clicked.connect(lambda: self.createNewFeature(self.ui.popSaveLE))
        self.ui.landuseSaveBrowseTB.clicked.connect(lambda: self.createNewFeature(self.ui.landuseSaveLE))
        self.ui.saveLandusePB.clicked.connect(lambda: self.createNewFeature(self.ui.landuseSaveLE))
        self.ui.elevationSaveBrowseTB.clicked.connect(lambda: self.createNewFeature(self.ui.elevationSaveLE))
        self.ui.saveElevationPB.clicked.connect(lambda: self.createNewFeature(self.ui.elevationSaveLE))

        self.ui.clearSelectionPB.clicked.connect(self.populateListView)
        self.ui.selectPrjRB.clicked.connect(self.updateSelectPrjCB)

        self.ui.runReprojectClipPB.clicked.connect(self.runClipAndReproject)
        self.ui.actionExit.setIcon(app.style().standardIcon(QStyle.SP_DialogCancelButton))

    def selectVectorFile(self, lineedit):
        # fileOptions = "Geopackage (*.gpkg);;Shapefile (*.shp);;All Files (*)"  # other file formats
        file, _ = QFileDialog.getOpenFileName(self, 'Select Vector File', "*.shp")
        if file:
            lineedit.setText(file)

    def selectRasterFile(self, lineedit):
        # fileOptions = "GeoTIFF (*.tif);;PNG (*.png);;JPEG (*.jpg);;All Files (*)"  # other file formats
        file, _ = QFileDialog.getOpenFileName(self, 'Select Raster File', "*.tif")
        if file:
            lineedit.setText(file)

    def selectClipFile(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Select Vector File', "*.shp")
        if file:
            self.ui.inputClipFtLE.setText(file)
            self.updateListFieldNameCB()

    def updateListFieldNameCB(self):
        """update selectPrj combo box with UTM spatial reference names"""

        fileName = self.ui.inputClipFtLE.text()
        access1 = access_mod_dataprep.AccessModDataPrep()
        try:
            fieldNames = access1.getValidFieldsForShapefile(fileName)
            print("Field Names:", fieldNames)
            self.ui.selectFieldNameCB.clear()
            self.ui.selectFieldNameCB.addItems(fieldNames)
            self.updateSelectFieldItems()
        except Exception as e:
            print("Error:", e)
            # Clear the combo box if there was an error
            self.ui.listFieldNameCB.clear()

    def updateSelectFieldItems(self):
        selectedField = self.ui.selectFieldNameCB.currentText()
        fileName = self.ui.inputClipFtLE.text()
        access1 = access_mod_dataprep.AccessModDataPrep()
        self.ui.targetClipFtCB.clear()
        items = access1.listFieldItems(fileName, selectedField)
        self.ui.targetClipFtCB.addItems(items)

    def displaySpatialRef(self):
        polyLineFile = self.ui.inputClipFtLE.text()
        access1 = access_mod_dataprep.AccessModDataPrep()
        access1.checkSpatialRef(polyLineFile)

        # opens a dialog box to create new polyline feature

    def createNewFeature(self, newFtLineEdit):
        dialog = SaveFileGui()  # Create an instance of saveFeatureWidget dialog
        if dialog.exec_() == QDialog.Accepted:  # Check if the dialog was accepted
            file = dialog.ui.newOutputFileLE.text()
            try:
                # self.ui.saveRoadLE.setText(file)
                newFtLineEdit.setText(file)
                self.ui.statusbar.showMessage("New shapefile has been created.")
            except Exception as e:
                self.ui.QMessageBox.information(self, 'Operation failed',
                                                'Creating new output shapefile failed with ' + str(
                                                    e.__class__) + ': ' + str(e),
                                                self.ui.QMessageBox.Ok)
                self.ui.statusbar.clearMessage()

    def openSavedFeature(self, saveFeatureLE):
        # filter_options = "GeoTIFF (*.tif);;PNG (*.png);;JPEG (*.jpg);;Geopackage (*.gpkg);;Shapefile (*.shp);;All " \
        # "Files (*)"  # other file formats
        file, _ = QFileDialog.getOpenFileName(self, 'Select File', "*.tif")
        if file:
            saveFeatureLE.setText(file)

    def updateSelectPrjCB(self):
        """update selectPrj combo box with UTM spatial reference names"""

        access2 = access_mod_dataprep.AccessModDataPrep()
        srsList = access2.listSpatialRef()
        self.ui.selectPrjCB.clear()
        if self.ui.selectPrjRB.isChecked():
            self.ui.selectPrjCB.addItems(srsList)

    def populateListView(self):
        # Clear the current items in the list view
        # print("running...") # test to see if method is being called
        self.ui.listPrjLW.clear()
        try:
            # Retrieve the text from each line edit and add it to the list view
            line_edit_list = [
                self.ui.saveRoadLE,
                self.ui.saveRiverLE,
                self.ui.saveProtectAreaLE,
                self.ui.saveHealthFacilLE,
                self.ui.saveWaterbodyLE
                # Add more line edits as needed
            ]
            access = access_mod_dataprep.AccessModDataPrep()
            for line_edit in line_edit_list:
                text = line_edit.text()
                if text:
                    srf = access.checkSpatialRef(text)
                    item = QListWidgetItem(srf)
                    # item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    # item.setCheckState(Qt.Checked)  # Set the initial state to checked
                    self.ui.listPrjLW.addItem(item)

        except Exception as e:
            print("Error in populateListView:", e)
            traceback.print_exc()  # Print the traceback for debugging

    def runClipAndReproject(self):
        try:
            inputFeatures = [self.ui.healthFacilLE.text(), self.ui.roadFileLE.text(), self.ui.riverLE.text(),
                             self.ui.waterbodyLE.text(), self.ui.protectedAreaLE.text(),
                             self.ui.populationFileLE.text(),
                             self.ui.landuseLE.text(), self.ui.elevationLE.text()]

            outputClipFeatures = [self.ui.saveHealthFacilLE.text(), self.ui.saveRoadLE.text(),
                                  self.ui.saveRiverLE.text(), self.ui.saveWaterbodyLE.text(),
                                  self.ui.saveProtectAreaLE.text(), self.ui.popSaveLE.text(),
                                  self.ui.landuseSaveLE.text(), self.ui.elevationSaveLE.text()]
            print(outputClipFeatures)

            clipFeature = self.ui.inputClipFtLE.text()

            # Check if the number of user inputs matches user outputs
            if len(inputFeatures) != len(outputClipFeatures):
                print("Error: Number of Vector input files and output names should be the same.")
                return

            targetCountyName = self.ui.targetClipFtCB.currentText()
            targetCountyNameField = self.ui.selectFieldNameCB.currentText()
            Crs = self.ui.selectPrjCB.currentText()
            outputCrs = arcpy.SpatialReference(Crs)
            print(outputCrs)

            # Create an instance of the VectorProjectAndClip class for vector data

            projectClipObjV = VectorProjectAndClip()
            # Create an instance of the RasterProjectAndClip class for Raster data
            projectClipObjR = RasterClipAndProject()
            targetCounty = projectClipObjV.selectTargetAdmin(clipFeature, targetCountyNameField, targetCountyName)

            # Loop through the clipped features and output files and perform clipping and projection
            for inputFeature, outputClipFeature in zip(inputFeatures, outputClipFeatures):
                # !!!!! this section was trying to explore the use of Describe to identify data types but failed to work
                # desc = arcpy.Describe(os.path(inputFeature)[1])
                # if desc.dataType == "Shapefile":
                #     print("The dataset is Shapefile")
                #
                #     # Call the clipFeature method to clip the input feature
                #     projectClipObjV.handleProjectAndClip(inputFeature, outputClipFeature, outputCrs, targetCounty)
                # elif desc.dataType == "RasterDataset":
                #     print("The dataset is a raster")
                #
                #     projectClipObjR.handleRasProjectAndClip(inputFeature, outputClipFeature, outputCrs, targetCounty)
                #
                # else:
                #     print("The dataset is neither raster nor shapefile")

                # use of file extension to identify vector files and raster files and applying the appropriate clip and
                # project method----------------------------------------------------------------------------------------

                file_extension = os.path.splitext(inputFeature)[1].lower()
                if file_extension == ".shp":
                    print("The dataset is Shapefile")

                    # Call the clipFeature method to clip the input feature
                    projectClipObjV.handleProjectAndClip(inputFeature, outputClipFeature, outputCrs, targetCounty)
                elif file_extension == ".tif":
                    print("The dataset is a raster")

                    projectClipObjR.handleRasProjectAndClip(inputFeature, outputClipFeature, outputCrs, targetCounty)

                else:
                    print("The dataset is neither raster nor shapefile")

        except Exception as e:
            # Print the error message and traceback to identify the issue
            print("Error occurred during clipping and projection:", e)
            traceback.print_exc()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainAppGui()
    form.show()
    app.exec_()
