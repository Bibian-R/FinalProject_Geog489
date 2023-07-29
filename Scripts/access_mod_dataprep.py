# import modules
import arcpy
import os

class AccessModDataPrep(object):
    def __init__(self):
        super(AccessModDataPrep, self).__init__()

    def listFieldNames(self, clipFeature):
        import arcpy
        fields = []

        fieldList = arcpy.ListFields(clipFeature)
        for field in fieldList:
            fields.append(field.name)
        return fields

    def getStringFieldsForDescribeObject(self, desc):
        """produces a list of editable string fields from a given arcpy.Describe object"""
        fields = []
        for field in desc.fields:  # go through all fields
            if field.type == 'String' and field.editable:
                fields.append(field.baseName)
        return fields

    def getValidFieldsForShapefile(self, fileName):
        """produces a list of editable string fields for a Point or Polygon shapefile with the given name; the list will be
         empty if no Point or Polygon based shapefile exists under that name."""
        import arcpy
        fields = []
        if os.path.exists(fileName):
            desc = arcpy.Describe(fileName)
            try:  # trying to access shapeType may throw exception for certain kinds of data sets
                if desc.shapeType in ['Point', 'Polygon', 'Polyline']:
                    fields = self.getStringFieldsForDescribeObject(desc)
            except:
                fields = []
        return fields

    def listFieldItems(self, clipFeature, selectedField):
        fieldsItems = []
        with arcpy.da.SearchCursor(clipFeature, (selectedField)) as cursor:
            for row in cursor:
                fieldsItems.append(row[0])
            return fieldsItems

    def selectTargetAdmin(self, clipFeature, nameField, county):
        try:
            whereClause = "{0} = '{1}'".format(arcpy.AddFieldDelimiters(clipFeature, nameField), county)

            targetCounty = arcpy.SelectLayerByAttribute_management(clipFeature, 'NEW_SELECTION', whereClause)

            # with arcpy.da.SearchCursor(targetCounty, (nameField)) as cursor:
            #     for row in cursor:
            #         # Print the name of all the counties in the selection
            #         print(row[0])
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
            return "Current SRS for {} : {} , '\n',""'you need to reproject'".format(desc.name,
                                                                                                           spatialRef.name)
        elif spatialRef.type == "Projected":
            return "Current SRS for {} : {} , '\n',""'confirm it's projected'".format(
                desc.name, spatialRef.name)

    @staticmethod
    # this method is meant to list all projected spatial reference system-----------------------------------------------
    def listSpatialRef():

        srs = arcpy.ListSpatialReferences("*UTM*", "PCS")
        srsList = []
        for sr in srs:
            cord = sr.split('/')[-1]
            srsList.append(cord)
        return srsList

# class that handles clipping and projection of vector data-------------------------------------------------------------
class VectorProjectAndClip(AccessModDataPrep):
    def __init__(self):
        super(VectorProjectAndClip, self).__init__()

    def project(self, clippedFeature, outputClipFeature, outputCrs):
        try:
            # Perform the projection
            arcpy.Project_management(clippedFeature, outputClipFeature, outputCrs)
            print("Feature has been projected successfully.")

        except Exception as e:
            print("Error occurred during projection:", e)

    def clipFeature(self, inputFile, targetCounty, outPut):
        try:
            arcpy.Clip_analysis(inputFile, targetCounty, outPut)
            print("Feature has been clipped successfully.")

        except Exception as e:
            print("Error occurred during clipping:", e)

    def selectTargetAdmin(self, clipFeature, nameField, county):
        # targetCounty = None  # Initialize the variable to none

        try:
            whereClause = "{0} = '{1}'".format(arcpy.AddFieldDelimiters(clipFeature, nameField), county)

            targetCounty = arcpy.SelectLayerByAttribute_management(clipFeature, 'NEW_SELECTION', whereClause)

            # with arcpy.da.SearchCursor(targetCounty, (nameField)) as cursor:
            #     for row in cursor:
            #         # Print the name of all the counties in the selection
            #         print(row[0])
            return targetCounty
        except Exception as e:
            print("Error occurred during target county selection:", e)
            print(arcpy.GetMessages())
            return None

    def handleProjectAndClip(self, inputFeatures, outputClipFeatures, outputCrs, targetCounty):
        arcpy.env.overwriteOutput = True

        tempClipped = r"C:\Users\brobert\OneDrive - Kemri Wellcome Trust\PennState\GEOG 489\Final " \
                      r"Project\Output\temp_clipped.shp"
        self.clipFeature(inputFeatures, targetCounty, tempClipped)

        # Create another temporary output feature class for projection
        tempOutput = r"C:\Users\brobert\OneDrive - Kemri Wellcome Trust\PennState\GEOG 489\Final " \
                     r"Project\Output\temp_output.shp"

        # Call the project function to project the clipped feature
        self.project(tempClipped, tempOutput, outputCrs)

        # Copy the projected feature to the final output feature class
        arcpy.CopyFeatures_management(tempOutput, outputClipFeatures)
        # print(out)
        # Clean up the temporary feature classes
        arcpy.Delete_management(tempClipped)
        arcpy.Delete_management(tempOutput)


# class that handles clipping and projection of raster data-------------------------------------------------------------
class RasterClipAndProject(AccessModDataPrep):
    def __init__(self):
        super(RasterClipAndProject, self).__init__()

    def projectRaster(self, inputRaster, outputRaster, outputCrs):
        try:
            arcpy.ProjectRaster_management(inputRaster, outputRaster, outputCrs)
            print("Raster has been projected successfully.")
        except Exception as e:
            print("Error occurred during raster projection:", e)

    def clipRaster(self, inputRaster, targetCounty, outputRaster):
        try:
            arcpy.Clip_management(inputRaster, "#", outputRaster, targetCounty, "#", "ClippingGeometry")
            print("Raster has been clipped successfully.")
        except Exception as e:
            print("Error occurred during raster clipping:", e)

    def handleRasProjectAndClip(self, inputRaster, outputClipRaster, outputCrs, targetCounty):
        arcpy.env.overwriteOutput = True
        # targetCountyObj = ProjectAndClip()
        # targetCounty = targetCountyObj.selectTargetAdmin(clipFeature,nameField,county)
        tempClipped = r"C:\Users\brobert\OneDrive - Kemri Wellcome Trust\PennState\GEOG 489\Final " \
                      r"Project\Output\temp_clipped.tif"
        self.clipRaster(inputRaster, targetCounty, tempClipped)

        # Create another temporary output feature class for projection
        tempOutput = r"C:\Users\brobert\OneDrive - Kemri Wellcome Trust\PennState\GEOG 489\Final " \
                     r"Project\Output\temp_output.tif"

        # Call the project function to project the clipped feature
        self.projectRaster(tempClipped, tempOutput, outputCrs)

        # Copy the projected feature to the final output feature class
        arcpy.CopyRaster_management(tempOutput, outputClipRaster)
        # print(out)
        # Clean up the temporary feature classes
        arcpy.Delete_management(tempClipped)
        arcpy.Delete_management(tempOutput)

    # Usage example:

#
# trial = AccessModDataPrep()
# trial1 = ProjectAndClip()
#
# #
# trial1.handleProjectAndClip(polyLineFile,outPut,newSrs)
# selected_feature = trial1.selectTargetAdmin(clipFeature, nameField, county)
# print(selected_feature)
# # trial = AccessModDataPrep()
# trial.listSpatialRef()
# trial.checkSpatialRef(rasterFile)
# trial1.clipFeature(polyLineFile,clipFeature,outPut)
# #trial.listFieldNames(clipFeature)
# trial.getValidFieldsForShapefile(clipFeature)
# trial.listFieldItems(clipFeature)
# trial.listSpatialRef()
# trial.project(outPut,roadPrj,newSrs)
# #trial.clipFeature(polyLineFile, targetCounty, outPut)
# trial.selectTargetAdmin(clipFeature, nameField, county)
# trial.checkSpatialRef(polyLineFile)
# trial.clipFeature(polyLineFile, targetCounty, outPut)
# selected_feature = trial.selectTargetAdmin(clipFeature, nameField, county)

# if selected_feature:
#     trial.clipFeature(polyLineFile, selected_feature, outPut)
# else:
#     print("Target feature not found.")

# outPut
# desc = arcpy.da.Describe(polyLineFile)
# keys_list = list(desc.keys())
# print(desc["dataType"], "\n", desc["name"])
# print(desc.keys)
# spatialRef = desc.SpatialReference
# print (spatialRef.Name)
# print(desc)
# outputClipFeature =  r"C:\Users\brobert\OneDrive - Kemri Wellcome Trust\PennState\GEOG 489\Final Project\Output\clip7.shp"
# outPut = r"C:\Users\brobert\OneDrive - Kemri Wellcome Trust\PennState\GEOG 489\Final Project\Output\clip20.shp"
# desc = arcpy.Describe(outPut)
# spatialRef = desc.SpatialReference
# print(spatialRef.Name)
#
# #roadPrj
# desc1 = arcpy.Describe(roadPrj)
# inputSRS1 = desc1.SpatialReference
# #nnn = inputSRS.Name
# print(inputSRS1.Name)
#
# #arcpy.Project_management(roadPrj, "testprj", newSrs)
# arcpy.env.workspace = r"C:\Users\brobert\OneDrive - Kemri Wellcome Trust\PennState\GEOG 489\Final Project\Output"
# feature_classes = arcpy.ListFeatureClasses()
# print(feature_classes)
#
