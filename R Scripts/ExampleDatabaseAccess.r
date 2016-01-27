# Brown bear database access using RODBC example
# Import RODBC library
library(RODBC)
# Create a connection object to the ODBC connection titled "ARCN Brown Bears"
Connection <-odbcConnect("ARCN Brown Bears")
# Retrieve the contents of the SurveyGroups table into a data frame
SurveyGroups <- sqlFetch(Connection, "SurveyGroups")B
# Retrieve bear groups data into a data frame by querying view
BearGroups <- sqlQuery(Connection, "SELECT [SurveyGroupName]
      ,[Unit]
      ,[CountOfUnitFlights]
      ,[GroupNumber]
      ,[CountOfGroupSightings]
      ,[FirstTailNo]
      ,[SecondTailNo]
      ,[FirstPlaneSaw]
      ,[SecondPlaneSaw]
      ,[BothPlanesSaw]
      ,[FirstAdults]
      ,[SecondAdults]
      ,[FirstCubs]
      ,[SecondCubs]
      ,[FirstWPInUnit]
      ,[SecondWPInUnit]
  FROM [CompositionCountSurveys].[dbo].[vwBearSightability]
  WHERE  CountOfUnitFlights = 2 And Not GroupNumber Is NULL")
# Close the database connection
close(Connection)
