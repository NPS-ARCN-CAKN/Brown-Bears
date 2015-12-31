# Brown bear database access using RODBC example
# Import RODBC library
library(RODBC)
# Create a connection object to the ODBC connection titled "ARCN Brown Bears"
Connection <-odbcConnect("ARCN Brown Bears")
# Retrieve the contents of the SurveyGroups table into a data frame
SurveyGroups <- sqlFetch(Connection, "SurveyGroups")
# Retrieve bear groups data into a data frame by querying view
BearGroups <- sqlQuery(Connection, "SELECT TOP 3 *  FROM vwBearGroups;")
# Close the database connection
close(Connection)
