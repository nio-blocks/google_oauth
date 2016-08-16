# Google Analytics
Collect data from Google Analytics and output to a signal.

## Properties
* **Reauthenticate Interval**: time in between authentications with Google
* **Additional Parameters**: any Google API optional parameters

## Dependencies
* [oauth2client](https://github.com/google/oauth2client)
* [RESTPolling Block](https://github.com/nio-blocks/http_blocks/blob/master/rest/rest_block.py)

## Commands
None

## Input
None

## Output
An output signal of the queried analytics data. Details of the Google Analytics data can be found [here](https://developers.google.com/analytics/devguides/reporting/core/v3/reference#data_response). The following is a sample of commonly included attributes, but note that not all will be included on every signal:
* kind
* id
* query
  - start-date
  - end-date
  - ids
  - filters
  - start-index
  - max-results
* itemsPerPage
* totalResults
* previousLink
* nextLink
* profileInfo
  - profileId
  - accountId
  - profileName
* columnHeaders
    - name
    - columnType
* rows

