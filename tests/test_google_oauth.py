from unittest.mock import patch

from nio.testing.block_test_case import NIOBlockTestCase

from ..google_oauth_block import GoogleOAuth


SAMPLE_GOOGLE_RESPONSE = \
    {'columnHeaders':
     [{'columnType': 'DIMENSION',
       'dataType': 'STRING',
       'name': 'ga:userType'},
      {'columnType': 'METRIC',
       'dataType': 'INTEGER',
       'name': 'ga:hits'},
      {'columnType': 'METRIC',
       'dataType': 'INTEGER',
       'name': 'ga:sessions'},
      {'columnType': 'METRIC',
       'dataType': 'INTEGER',
       'name': 'ga:users'}],
     'containsSampledData': False,
     'id': 'long_id_string_goes_here',
     'itemsPerPage': 1000,
     'kind': 'analytics#gaData',
     'profileInfo': {'accountId': 'acct_id',
                     'internalWebPropertyId': 'web_id',
                     'profileId': 'profile_id',
                     'profileName': 'All Web Site Data',
                     'tableId': 'table_id',
                     'webPropertyId': 'prop_id'},
     'query': {'dimensions': 'ga:userType',
               'end-date': '2014-10-20',
               'ids': 'id_string',
               'max-results': 1000,
               'metrics': ['ga:hits', 'ga:sessions', 'ga:users'],
               'start-date': '2014-10-06',
               'start-index': 1},
     'rows': [['New Visitor', '1489', '1157', '1157'],
              ['Returning Visitor', '2057', '1050', '340']],
     'selfLink': 'long_link_string_goes_here',
     'totalResults': 2,
     'totalsForAllResults': {'ga:hits': '3546',
                             'ga:sessions': '2207',
                             'ga:users': '1497'}}


class TestGoogleOAuth(NIOBlockTestCase):

    def test_pretty_results(self):
        """ Test that results can get parsed correctly """
        block = GoogleOAuth()
        with patch.object(block, '_authenticate'):
            self.configure_block(block, {
                "pretty_results": True
            })

        sigs_out = block._get_signals_from_results(SAMPLE_GOOGLE_RESPONSE)

        # We want two signals, not one when it's pretty
        self.assertEqual(len(sigs_out), 2)

        # Assert integers got parsed
        sig_1 = sigs_out[0]
        self.assertIsInstance(getattr(sig_1, 'ga:userType'), str)
        self.assertIsInstance(getattr(sig_1, 'ga:hits'), int)

    def test_no_pretty_results(self):
        """ Test that unchecking the box does not parse results """
        block = GoogleOAuth()
        with patch.object(block, '_authenticate'):
            self.configure_block(block, {
                "pretty_results": False
            })

        sigs_out = block._get_signals_from_results(SAMPLE_GOOGLE_RESPONSE)

        # We just want the original response when it's not pretty
        self.assertEqual(len(sigs_out), 1)
        self.assertIsNotNone(sigs_out[0].columnHeaders)

    def test_addl_params(self):
        block = GoogleOAuth()
        with patch.object(block, '_authenticate'):
            self.configure_block(block, {
                "addl_params": [
                    {
                        "prop_name": "param1",
                        "prop_value": "value1"
                    },
                    {
                        "prop_name": "param2",
                        "prop_value": "value2"
                    }
                ]
            })

        params = block.get_addl_params()
        self.assertEqual(params['param1'], 'value1')
        self.assertEqual(params['param2'], 'value2')
