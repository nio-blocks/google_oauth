GoogleOAuth
===========
Collect data from Google Analytics and output to a signal.

Properties
----------
- **addl_params**: Google APIs tend to have many optional additional paramters. This property allows a configurer to add and remove optional parameters with minimal overhead. To use these properties, just call the get_addl_params method when reporting url parameters in the subclass
- **include_query**: Whether to include queries on polling requests.
- **key_config_file**: Location of private key.
- **polling_interval**: Time between polling requests.
- **pretty_results**: # Whether or not to return readable results from Google. The raw response contains richer information but is harder to parse. By checking this, the results will be parsed and split into more readable signals. Recommended to be checked unless you need some advanced information from the Google API
- **queries**: Queries to include on request data.
- **reauth_interval**: Time in between authentications with Google
- **retry_interval**: Time between retries for authentication
- **retry_limit**: Max number of times to retry authentication

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: An output signal of the queried analytics data. Details of the Google Analytics data can be found [here](https://developers.google.com/analytics/devguides/reporting/core/v3/reference#data_response).

Commands
--------
None

Dependencies
------------
None
