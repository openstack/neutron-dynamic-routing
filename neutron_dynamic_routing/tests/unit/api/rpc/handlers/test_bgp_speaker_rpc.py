# Copyright 2016 Huawei Technologies India Pvt. Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import mock

from neutron.tests import base
from neutron_lib.api.definitions import bgp as bgp_ext
from neutron_lib.plugins import directory

from neutron_dynamic_routing.api.rpc.handlers import bgp_speaker_rpc


class TestBgpSpeakerRpcCallback(base.BaseTestCase):

    def setUp(self):
        super(TestBgpSpeakerRpcCallback, self).setUp()
        self.plugin = mock.Mock()
        directory.add_plugin(bgp_ext.ALIAS, self.plugin)
        self.callback = bgp_speaker_rpc.BgpSpeakerRpcCallback()

    def test_get_bgp_speaker_info(self):
        self.callback.get_bgp_speaker_info(mock.Mock(),
                                           bgp_speaker_id='id1')
        self.assertIsNotNone(len(self.plugin.mock_calls))

    def test_get_bgp_peer_info(self):
        self.callback.get_bgp_peer_info(mock.Mock(),
                                        bgp_peer_id='id1')
        self.assertIsNotNone(len(self.plugin.mock_calls))

    def test_get_bgp_speakers(self):
        self.callback.get_bgp_speakers(mock.Mock(),
                                       host='host')
        self.assertIsNotNone(len(self.plugin.mock_calls))
