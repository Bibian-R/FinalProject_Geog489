# -*- Geoprocessing classes for AccessMod Data Prep Creator App -*-
# -*- By: Bibian Robert -*-
# -*- GEOG 489: Final Project -*-
# ***** Script Description ******

# This code contains AccessModDataPrep class derived from arcpy module, that contains methods that does
# geospatial data processing and provides functionality to select vector and raster files, perform clipping
# and projection, and save output files.
#  The AccessModataPrep class contains general methods including:
# listFieldNames:
# getStringFieldsForDescribeObject
# listFieldItems:
# getValidFieldsForShapefile:
# selectTargetAdmin:
# checkSpatialRef:
# listSpatialRef():

# There are two additional child classes of AccessModDataPrep class that class VectorProjectAndClip(AccessModDataPrep)
# that handles geoprocessing for vector data and class RasterClipAndProject(AccessModDataPrep) that handles
# geoprocessing for raster data.

# class VectorProjectAndClip(AccessModDataPrep) has the following methods:.
# def projectVector: projects vector data to a projected coordinate system
# def clipVector: clip vector data to target clip area
# def handleVecProjectAndClip : clips, reproject and saves new vector file

# class RasterClipAndProject(AccessModDataPrep)(AccessModDataPrep) has the following methods:.
# def rasProject: projects raster data to a projected coordinate system
# def clipFeature: clip raster data to target clip area
# def handleRasProjectAndClip : clips, reproject and saves new raster file

# import modules
import arcpy
import os


class AccessModDataPrep(object):
    def __init__(self):
        super(AccessModDataPrep, self).__init__()

    def listFieldNames(self, clipFeature):
        """The listFieldNames method takes the path to a vector dataset (feature class or shapefile) as clipFeature and
        returns a list of field names present in that dataset."""
        import arcpy
        fields = []

        fieldList = arcpy.ListFields(clipFeature)
        for field in fieldList:
            fields.append(field.name)
        return fields

    def getStringFieldsForDescribeObject(self, desc):
        """method takes a desc object as an input obtained from Describe function and returns a list of
         names of string-type fields from the provided desc object."""
        fields = []
        for field in desc.fields:  # go through all fields
            if field.type == 'String' and field.editable:
                fields.append(field.baseName)
        return fields

    def getValidFieldsForShapefile(self, clipFeature):
        """method takes path to a shapefile (clipFeature) as parameter and returns a list of valid
        string-type fields for the shapefile."""
        import arcpy
        fields = []
        if os.path.exists(clipFeature):
            desc = arcpy.Describe(clipFeature)
            try:  # trying to access shapeType may throw exception for certain kinds of data sets
                if desc.shapeType in ['Polygon']:
                    fields = self.getStringFieldsForDescribeObject(desc)
            except Exception as e:
                print(e)
                #fields = []
        return fields

    def listFieldItems(self, clipFeature, selectedField):
        """produces a list of items for the selected Field Name"""
        fieldsItems = []
        with arcpy.da.SearchCursor(clipFeature, (selectedField)) as cursor:
            for row in cursor:
                fieldsItems.append(row[0])
            return fieldsItems

    def selectTargetAdmin(self, clipFeature, nameField, county):
        """produces a list of items for the selected Field Name"""
        try:
            whereClause = "{0} = '{1}'".format(arcpy.AddFieldDelimiters(clipFeature, nameField), county)

            targetCounty = arcpy.SelectLayerByAttribute_management(clipFeature, 'NEW_SELECTION', whereClause)

            return targetCounty
        except Exception as e:
            print(e)
            print(arcpy.GetMessages())

    # Check the spatial reference of the feature selected
    def checkSpatialRef(self, inputFeature):
        desc = arcpy.Describe(inputFeature)
        spatialRef = desc.spatialReference

        if spatialRef.name == "Unknown":
            return "{} has an unknown spatial reference".format(desc.name)  # print
        # Otherwise, print out the feature class name and spatial reference
        elif spatialRef.type == "Geographic":
            return "Current SRS for {} : {} , '\n',""'you need to reproject'".format(desc.name, spatialRef.name)
        elif spatialRef.type == "Projected":
            return "Current SRS for {} : {} , '\n',""'confirm it's projected'".format(
                desc.name, spatialRef.name)

    @staticmethod
    # this method takes no parameter & lists all projected UTM coordinate reference system and is called directly on
    # the class without creating an instance of the class-----------------------------------------------------
    def listSpatialRef():
        """ obtain a list of spatial reference systems (SRS) with names containing "UTM" and are of type "Projected
        Coordinate System" (PCS). It then processes the obtained spatial reference systems to extract the names and
        returns them as a list."""

        srs = arcpy.ListSpatialReferences("*UTM*", "PCS")
        srsList = []
        for sr in srs:
            cord = sr.split('/')[-1]  # extract the name of the PCS by taking last part of the  splitting the SRS string
            srsList.append(cord)
        return srsList


# class that handles clipping and projection of vector data-------------------------------------------------------------
class VectorProjectAndClip(AccessModDataPrep):
    def __init__(self):
        super(VectorProjectAndClip, self).__init__()

    # method that projects vector data---
    def projectVector(self, clippedFeature, outputClipFeature, outputCrs):
        try:
            # Perform the projection of vector data---
            arcpy.Project_management(clippedFeature, outputClipFeature, outputCrs)
            print("Feature has been projected successfully.")

        except Exception as e:
            print("Error occurred during projection:", e)

    # method that clips vector data---
    def clipVector(self, inputFile, targetCounty, outPut):
        try:
            arcpy.Clip_analysis(inputFile, targetCounty, outPut)  # performs clipping
            print("Feature has been clipped successfully.")

        except Exception as e:
            print("Error occurred during clipping:", e)

    # method that handles both clipping and projection of the same vector file
    def handleVecProjectAndClip(self, inputFeatures, outputClipFeatures, outputCrs, targetCounty):
        arcpy.env.overwriteOutput = True  # overwrites any existing file with similar names
        # Create a temporary output clip feature class for clipping and saved on temporary local disk---
        tempClipped = r"C:\Users\brobert\OneDrive - Kemri Wellcome Trust\PennState\GEOG 489\Final " \
                      r"Project\Output\temp_clipped.shp"
        # call the clipFeature method for clipping---
        self.clipVector(inputFeatures, targetCounty, tempClipped)  # clips feature and saved temporarily

        # # Create a temporary output reproject feature class for projection and saved on temporary local disk---
        tempOutput = r"C:\Users\brobert\OneDrive - Kemri Wellcome Trust\PennState\GEOG 489\Final " \
                     r"Project\Output\temp_output.shp"

        # Call the project function to project the clipped feature---
        self.projectVector(tempClipped, tempOutput, outputCrs)  # projects the temp clipped feature and saved temporarily

        # Copy the projected Vector feature to the final output feature class---
        arcpy.CopyFeatures_management(tempOutput, outputClipFeatures)

        # Clean up the temporary feature classes
        arcpy.Delete_management(tempClipped)
        arcpy.Delete_management(tempOutput)


# class that handles clipping and projection of raster data-------------------------------------------------------------
class RasterClipAndProject(AccessModDataPrep):
    def __init__(self):
        super(RasterClipAndProject, self).__init__()

    # method that projects raster data---
    def projectRaster(self, inputRaster, outputRaster, outputCrs):
        try:
            arcpy.ProjectRaster_management(inputRaster, outputRaster, outputCrs)
            print("Raster has been projected successfully.")
        except Exception as e:
            print("Error occurred during raster projection:", e)

    # method that clips raster data---
    def clipRaster(self, inputRaster, targetCounty, outputRaster):
        try:
            arcpy.Clip_management(inputRaster, "#", outputRaster, targetCounty, "#", "ClippingGeometry")
            print("Raster has been clipped successfully.")
        except Exception as e:
            print("Error occurred during raster clipping:", e)

    # method that handles both clipping and projection of the same Raster file---
    def handleRasProjectAndClip(self, inputRaster, outputClipRaster, outputCrs, targetCounty):
        arcpy.env.overwriteOutput = True
        # Create a temporary output clip feature class for clipping---
        tempClipped = r"C:\Users\brobert\OneDrive - Kemri Wellcome Trust\PennState\GEOG 489\Final " \
                      r"Project\Output\temp_clipped.tif"
        # Call the clipRaster method for clipping---
        self.clipRaster(inputRaster, targetCounty, tempClipped)

        # Create a temporary output feature class for projection---
        tempOutput = r"C:\Users\brobert\OneDrive - Kemri Wellcome Trust\PennState\GEOG 489\Final " \
                     r"Project\Output\temp_output.tif"

        # Call the project function to project the clipped feature
        self.projectRaster(tempClipped, tempOutput, outputCrs)

        # Copy the projected Raster feature to the final output feature class---
        arcpy.CopyRaster_management(tempOutput, outputClipRaster)
        # print(out)
        # Clean up the temporary feature classes
        arcpy.Delete_management(tempClipped)
        arcpy.Delete_management(tempOutput)
