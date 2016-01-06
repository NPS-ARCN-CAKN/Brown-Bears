# BearWaypointsToSQL.py
# Purpose: A Python script used by the National Park Service Arctic Network
# brown bear monitoring program.  Exports pilot's or observer's waypoints collected during aerial surveys
# to SQL insert queries suitable for importing the data into the program's master monitoring database.

# This Python script loops through the records in the waypoints shapefile and writes an SQL insert query
# for each record.  Each insert query is sequentially appended to an output sql script file that is named
# the same as the input shapefile with an '.sql' suffix.

# Notes on using the script:
# This script does not interact with the database in any way; it just exports .sql scripts, so there is
# no danger of database corruption to test-running the script.
# The script is designed to be run via an ArcGIS toolbox tool.

# IMPORTANT NOTE: The SQL insert queries are wrapped in unclosed transaction statements (the transaction is started,
# but not finished with either a COMMIT or ROLLBACK statement).  The transaction ensures that either all the records
# are inserted or none of the records are inserted (e.g. if any query fails then they all fail). You must COMMIT or
# ROLLBACK the transaction after running the script or the database will be left in a locked state.

# Written by Scott D. Miller, Data Manager, Arctic and Central Alaska Inventory and Monitoring Networks, December, 2015

# import libraries
import arcpy
import os

# get the parameters from the arctoolbox wrapper
surveyid = arcpy.GetParameterAsText(1) # SurveyID
waypointfile = arcpy.GetParameterAsText(0)# Source of the GPS waypoints

# Output SQL script file
OutputFile = waypointfile + '.sql'
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
file.write("-- Insert queries to transfer pilot waypoints to ARCN bear monitoring database\n")
file.write("-- File generated " + executiontime + " by " + user + "\n")
file.write("USE CompositionCountSurveys \n")
file.write("BEGIN TRANSACTION -- Do not forget to COMMIT or ROLLBACK the changes after executing or the database will be in a locked state \n")
file.write("SET QUOTED_IDENTIFIER ON\n\n")
file.write("\n-- insert the generated waypoints from " + waypointfile + " -----------------------------------------------------------\n")
file.write("DECLARE @SurveyID nvarchar(50) -- SurveyID of the record in the Surveys table to which the transects below will be related\n")
file.write("SET @SurveyID = '" + surveyid + "'\n")

# the arcpy.da tools don't really have strong typing so we can't refer to columns by name making our job difficult.
# convert the feature class to a Python array so we can refer to the data columns we want to access by column name
arr = arcpy.da.FeatureClassToNumPyArray(waypointfile, ('ident', 'ltime','altitude','model','temp','comment','Latitude', 'Longitude'))

# loop through the array
for row in arr:
    # the variables below correspond to the column names in the database Locations table.
    # these variables will be used to map data from the waypoints file into those needed for an SQL insert query
    LocationName = row["ident"]
    Type = "WAYPOINT"
    CaptureDate = row["ltime"]
    Altitude = row["altitude"]
    Temperature = row["temp"]
    GPSModel = row["model"]
    PointFileName = str(os.path.basename(waypointfile))
    Notes = row["comment"]
    Lat = row["Latitude"]
    Lon = row["Longitude"]
    Geog = "geography::STPointFromText('POINT(" + str(Lon) + " " + str(Lat) + ")', 4326)"

    # create the sql insert query and substitute the data from the waypoints file into the values portion
    sql = "INSERT INTO [CompositionCountSurveys].[dbo].[Locations]" + \
        "([LocationName]," + \
        "[Type]," + \
        "[CaptureDate]," + \
        "[Altitude]," + \
        "[Temperature]," + \
        "[GPSModel]," + \
        "[PointFilename]," + \
        "[Notes]," + \
        "[Location]," + \
        "[SurveyID])" + \
        "VALUES" + \
        "('" + str(LocationName) + "'," + \
        "'" + str(Type) + "'," + \
        "'" + str(CaptureDate) + "'," + \
        str(Altitude) + "," + \
        str(Temperature) + "," + \
        "'" + str(GPSModel) + "'," + \
        "'" + str(PointFileName) + "'," + \
        "'" + str(Notes) + "'," + \
        Geog + "," + \
        "@SurveyID)\n"

    # write the query to standard output
    arcpy.AddMessage(sql)

    # write the query to the sql script file
    file.write(sql)

# commit/rollback reminder
file.write("-- Do not forget to COMMIT or ROLLBACK the changes after executing or the database will be in a locked state \n")

# a convenience query for checking the inserted records
file.write("-- Execute the query below after committing records to retrieve the inserted records\n")
file.write("-- SET @SurveyID = '" + surveyid + "'\n")
file.write("-- SELECT * FROM Locations WHERE SurveyID = @SurveyID;\n")

# close the output file
file.close()
arcpy.AddMessage('Done\n')
arcpy.AddMessage('SQL insert query script available at ' + OutputFile + '\n')