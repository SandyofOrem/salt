# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Mike Place <mp@saltstack.com>`
'''

# Import python libs
from __future__ import absolute_import, unicode_literals

# Import Salt Testing libs
import tests.integration as integration
from tests.support.unit import TestCase, skipIf
from tests.support.mock import patch, NO_MOCK, NO_MOCK_REASON

# Import Salt libs
from salt import client
from salt.exceptions import EauthAuthenticationError, SaltInvocationError, SaltClientError


@skipIf(NO_MOCK, NO_MOCK_REASON)
class LocalClientTestCase(TestCase,
                          integration.SaltClientTestCaseMixin):

    def test_create_local_client(self):
        local_client = client.LocalClient(mopts=self.get_temp_config('master'))
        self.assertIsInstance(local_client, client.LocalClient, 'LocalClient did not create a LocalClient instance')

    def test_check_pub_data(self):
        just_minions = {'minions': ['m1', 'm2']}
        jid_no_minions = {'jid': '1234', 'minions': []}
        valid_pub_data = {'minions': ['m1', 'm2'], 'jid': '1234'}

        self.assertRaises(EauthAuthenticationError, self.client._check_pub_data, '')
        self.assertDictEqual({},
            self.client._check_pub_data(just_minions),
            'Did not handle lack of jid correctly')

        self.assertDictEqual(
            {},
            self.client._check_pub_data({'jid': '0'}),
            'Passing JID of zero is not handled gracefully')

        with patch.dict(self.client.opts, {}):
            self.client._check_pub_data(jid_no_minions)

        self.assertDictEqual(valid_pub_data, self.client._check_pub_data(valid_pub_data))

    def test_cmd_subset(self):
        with patch('salt.client.LocalClient.cmd', return_value={'minion1': ['first.func', 'second.func'],
                                                                'minion2': ['first.func', 'second.func']}):
            with patch('salt.client.LocalClient.cmd_cli') as cmd_cli_mock:
                self.client.cmd_subset('*', 'first.func', sub=1, cli=True)
                try:
                    cmd_cli_mock.assert_called_with(['minion2'], 'first.func', (), progress=False,
                                                    kwarg=None, tgt_type='list',
                                                    ret='')
                except AssertionError:
                    cmd_cli_mock.assert_called_with(['minion1'], 'first.func', (), progress=False,
                                                    kwarg=None, tgt_type='list',
                                                    ret='')
                self.client.cmd_subset('*', 'first.func', sub=10, cli=True)
                try:
                    cmd_cli_mock.assert_called_with(['minion2', 'minion1'], 'first.func', (), progress=False,
                                                    kwarg=None, tgt_type='list',
                                                    ret='')
                except AssertionError:
                    cmd_cli_mock.assert_called_with(['minion1', 'minion2'], 'first.func', (), progress=False,
                                                    kwarg=None, tgt_type='list',
                                                    ret='')

    def test_pub(self):
        if self.get_config('minion')['transport'] != 'zeromq':
            self.skipTest('This test only works with ZeroMQ')
        # Make sure we cleanly return if the publisher isn't running
        with patch('os.path.exists', return_value=False):
            self.assertRaises(SaltClientError, lambda: self.client.pub('*', 'test.ping'))

        # Check nodegroups behavior
        with patch('os.path.exists', return_value=True):
            with patch.dict(self.client.opts,
                            {'nodegroups':
                                 {'group1': 'L@foo.domain.com,bar.domain.com,baz.domain.com or bl*.domain.com'}}):
                # Do we raise an exception if the nodegroup can't be matched?
                self.assertRaises(SaltInvocationError,
                                  self.client.pub,
                                  'non_existent_group', 'test.ping', tgt_type='nodegroup')
