from nio.metadata.properties import BoolProperty, ListProperty, \
    PropertyHolder, StringProperty, TimeDeltaProperty
from nio.common.signal.base import Signal
from nio.modules.scheduler import Job
from urllib.parse import urlencode
from .http_blocks.rest.rest_block import RESTPolling
from .oauth2_mixin.oauth2 import OAuth2, OAuth2Exception


class URLParameter(PropertyHolder):
    prop_name = StringProperty(title="Property Name")
    prop_value = StringProperty(title="Property Value")


class GoogleOAuth(OAuth2, RESTPolling):

    _URL_PREFIX = 'https://www.googleapis.com/'

    # Whether or not to return readable results from Google
    # The raw response contains richer information but is harder to parse.
    # By checking this, the results will be parsed and split into more
    # readable signals. Recommended to be checked unless you need some
    # advanced information from the Google API
    pretty_results = BoolProperty(title="Pretty Results", default=True)

    # Google APIs tend to have many optional additional paramters. This
    # property allows a configurer to add and remove optional parameters with
    # minimal overhead. To use these properties, just call the get_addl_params
    # method when reporting url parameters in the subclass
    addl_params = ListProperty(
        URLParameter, title="Additional Parameters", default=[])

    # We should periodically re-authenticate with Google, this is the interval
    # to do so.
    # Ideally, we use the expiry time in the OAuth token that we get back, but
    # that will require a non-backwards compatible change to the OAuth2 mixin,
    # so for now, having an extra non-visible property will have to do
    reauth_interval = TimeDeltaProperty(
        title="Reauthenticate Interval",
        visible=False,
        default={'seconds': 2400})  # Default to 40 mins

    def __init__(self):
        super().__init__()
        self._access_token = None
        self._reauth_job = None

    def get_google_scope(self):
        """ This should be implemented by the base block and return the
        scope needed for API access """
        return NotImplemented

    def get_url_suffix(self):
        """ Return the URL suffix to be appended, without the leading slash.

        Will probably have a form similar to this:
        analytics/v3/data/ga
        """
        return NotImplemented

    def get_url_parameters(self):
        """ Return a dictionary containing URL parameters to include """
        return dict()

    def get_addl_params(self):
        """ Return a dictionary of any additional configured URL parameters """
        params = dict()
        for param in self.addl_params:
            params[param.prop_name] = param.prop_value
        return params

    def _authenticate(self):
        """Overridden from RESTPolling block - Obtain and set access token"""
        try:
            self._access_token = self.get_access_token(self.get_google_scope())
            self._logger.debug("Obtained access token {0}".format(
                self._access_token))

            if self._reauth_job:
                self._reauth_job.cancel()

            # Remember to reauthenticate at a certain point if it's configured
            if self.reauth_interval.total_seconds() > 0:
                self._reauth_job = Job(
                    self._authenticate, self.reauth_interval, False)

        except OAuth2Exception as oae:
            self._logger.error(
                "Error obtaining access token : {0}".format(oae))
            self._access_token = None

    def _prepare_url(self, paging=False):
        """ Overridden - Build the request URL and headers for the request """
        self._url = "{0}{1}?{2}".format(
            self._URL_PREFIX,
            self.get_url_suffix(),
            urlencode(self.get_url_parameters()))

        headers = {
            "Content-Type": "application/json"
        }
        headers.update(self.get_access_token_headers(self._access_token))
        return headers

    def _process_response(self, resp):
        """ Overridden from parent - make sure we got a 200 and valid JSON """
        status = resp.status_code
        if status != 200:
            self._logger.error("Status {0} returned while requesting : {1}"
                               .format(status, resp))
        return self._get_signals_from_results(resp.json()), False

    def _get_signals_from_results(self, results):
        """ Returns a list of signals based on a results dictionary.

        If prett_results is checked, do some parsing here and spit out
        individual signals for every row. See unit test for examples
        """
        if not isinstance(results, dict):
            raise TypeError("Results were not parsed properly")

        if not self.pretty_results:
            return [Signal(results)]

        column_information = results.get('columnHeaders', [])
        self._logger.debug(
            "Building signals using columns {0}".format(column_information))

        signals = [
            Signal(self._build_signal_dictionary(column_information, row))
            for row in results.get('rows', [])]

        return signals

    def _build_signal_dictionary(self, columns, row):
        """Build a signal from a particular row based on column information"""
        sig_out = dict()
        for index, col in enumerate(columns):
            if col.get('dataType') == 'INTEGER':
                sig_out[col['name']] = int(row[index])
            else:
                sig_out[col['name']] = row[index]

        return sig_out
