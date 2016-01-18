# SurveyUnitsToSQL.py
# Purpose: A Python script used by the National Park Service Arctic Network
# brown bear monitoring program.  This script was written to transform the polygon survey unit features
# from shapefiles of survey units into
# SQL insert queries suitable for importing the data into the program's master monitoring database.

# This Python script loops through the records in the submitted shapefile and writes an SQL insert query
# for each record.  Each insert query is sequentially appended to an output sql script file that is named
# the same as the input shapefile with an '.sql' suffix.

# IMPORTANT NOTE: The SQL insert queries are wrapped in unclosed transaction statements (the transaction is started,
# but not finished with either a COMMIT or ROLLBACK statement).  The transaction ensures that either all the records
# are inserted or none of the records are inserted (e.g. if any query fails then they all fail). You must COMMIT or
# ROLLBACK the transaction after running the script or the database will be left in a locked state.

# Written by Scott D. Miller, Data Manager, Arctic and Central Alaska Inventory and Monitoring Networks, December, 2015

# import libraries
import arcpy

# get the parameters
SurveyGroupID = 'D37FFF9F-6202-4C75-9AA8-0B94AF59C33A' #arcpy.GetParameterAsText(1) # SurveyGroupID
# InputFile = r'C:\Work\VitalSigns\ARCN Brown Bears\Data\2015_BearSurvey_SewardPen-BELA\Deliverable BB-05-SurveyUnits\BELA_SP_2013_AllSurveyUnits.shp' #arcpy.GetParameterAsText(0)# Source of the GPS Tracklog
InputFile = r'C:\Work\WEAR Wildlife Datasets Documentation and Archival\Datasets\WEAR-004-2010 Bear Survey GAAR 2010\GAAR 2010\data\Data_Forms\card files\gaar_su.shp'

# Output SQL script file
OutputFile = InputFile + '.sql'
file = open(OutputFile, "w") # open the file

# gather some metadata to put in the sql scripts
# current time
import time
ow = time.strftime("%c") # date and time
executiontime = time.strftime("%c")

# username
import getpass
user = getpass.getuser()

# write some metadata to the sql script
file.write("-- Insert queries to transfer 2013 BELA bear survey units to the master monitoring database\n")
file.write("-- File generated " + executiontime + " by " + user + "\n")
file.write("USE CompositionCountSurveys \n")
file.write("BEGIN TRANSACTION -- Do not forget to COMMIT or ROLLBACK the changes after executing or the database will be in a locked state \n")
file.write("SET QUOTED_IDENTIFIER ON\n\n")
file.write("\n-- insert the generated transects from " + InputFile + " -----------------------------------------------------------\n")
file.write("DECLARE @SurveyGroupID nvarchar(50) -- SurveyGroupID of the record in the SurveyGroups table to which the units below will be related\n")
file.write("SET @SurveyGroupID = '" + SurveyGroupID + "'\n")

# the arcpy.da tools don't really have strong typing so we can't refer to columns by name making our job difficult.
# convert the feature class to a Python array so we can refer to the data columns we want to access by column name
with arcpy.da.SearchCursor(InputFile,["Shape@","UniqueID"]) as sc:
    for row in sc:
        Shape = row[0]
        Unit = row[1]
        WKT = Shape.WKT
        Feature = "geography::STPolyFromText('" + WKT.replace('MULTIPOLYGON','POLYGON') + "', 4326)" # sql server geography doesn't recognize multipolygon
        # somehow an extra set of parentheses gets in there
        Feature = Feature.replace('(((','((')
        Feature = Feature.replace(')))','))')

        #create the sql insert query and substitute the data from the waypoints file into the values portion
        sql = "INSERT INTO SurveyUnits(" + \
            "[Unit]," + \
            "[Feature]," + \
            "[SurveyGroupID])" + \
            "VALUES" + \
            "('" + str(Unit) + "'," + \
            Feature + "," + \
            "@SurveyGroupID)\n"

        # write the query to the sql script file
        file.write(sql)

# commit/rollback reminder
file.write("-- Do not forget to COMMIT or ROLLBACK the changes after executing or the database will be in a locked state \n")

# a convenience query for checking the inserted records
file.write("-- Execute the query below after committing records to retrieve the inserted records\n")
file.write("-- SET @SurveyGroupID = '" + SurveyGroupID + "'\n")
file.write("-- SELECT * FROM SurveyUnits WHERE SurveyGroupID = @SurveyGroupID;\n")

# close the output file
file.close()
arcpy.AddMessage('Done\n')
Message = 'SQL insert query script available at ' + OutputFile + '\n'
arcpy.AddMessage(Message)
print Message
