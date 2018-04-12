# Copyright (C) 2017 VA Linux Systems Japan K.K.
# Copyright (C) 2017 Fumihiko Kakuma <kakuma at valinux co jp>
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from neutron.tests import base
from neutron_lib.callbacks import events
from neutron_lib.callbacks import registry
from neutron_lib.callbacks import resources

from neutron_dynamic_routing.api.rpc.callbacks import resources as dr_resources
from neutron_dynamic_routing.db import bgp_db
from neutron_dynamic_routing.services.bgp import bgp_plugin


class TestBgpPlugin(base.BaseTestCase):

    def setUp(self):
        super(TestBgpPlugin, self).setUp()
        bgp_notify_p = mock.patch('neutron_dynamic_routing.api.rpc.'
                                  'agentnotifiers.bgp_dr_rpc_agent_api.'
                                  'BgpDrAgentNotifyApi')
        bgp_notify_p.start()
        rpc_conn_p = mock.patch('neutron.common.rpc.Connection')
        rpc_conn_p.start()
        admin_ctx_p = mock.patch('neutron_lib.context.get_admin_context')
        self.admin_ctx_m = admin_ctx_p.start()
        self.fake_admin_ctx = mock.Mock()
        self.admin_ctx_m.return_value = self.fake_admin_ctx
        self.plugin = bgp_plugin.BgpPlugin()

    def _create_test_payload(self, context='test_ctx'):
        bgp_speaker = {'id': '11111111-2222-3333-4444-555555555555'}
        payload = {'plugin': self.plugin, 'context': context,
                   'bgp_speaker': bgp_speaker}
        return payload

    def test__register_callbacks(self):
        with mock.patch.object(registry, 'subscribe') as subscribe:
            plugin = bgp_plugin.BgpPlugin()
            expected_calls = [
                mock.call(plugin.bgp_drscheduler.schedule_bgp_speaker_callback,
                          dr_resources.BGP_SPEAKER, events.AFTER_CREATE),
                mock.call(plugin.floatingip_update_callback,
                          resources.FLOATING_IP, events.AFTER_UPDATE),
                mock.call(plugin.router_interface_callback,
                          resources.ROUTER_INTERFACE, events.AFTER_CREATE),
                mock.call(plugin.router_interface_callback,
                          resources.ROUTER_INTERFACE, events.BEFORE_CREATE),
                mock.call(plugin.router_interface_callback,
                          resources.ROUTER_INTERFACE, events.AFTER_DELETE),
                mock.call(plugin.router_gateway_callback,
                          resources.ROUTER_GATEWAY, events.AFTER_CREATE),
                mock.call(plugin.router_gateway_callback,
                          resources.ROUTER_GATEWAY, events.AFTER_DELETE),
            ]
            self.assertEqual(subscribe.call_args_list, expected_calls)

    def test_create_bgp_speaker(self):
        test_context = 'create_bgp_context'
        test_bgp_speaker = {'id': None}
        payload = self._create_test_payload(context=test_context)
        with mock.patch.object(bgp_db.BgpDbMixin,
                               'create_bgp_speaker') as create_bgp_sp:
            with mock.patch.object(registry, 'notify') as notify:
                create_bgp_sp.return_value = payload['bgp_speaker']
                self.assertEqual(self.plugin.create_bgp_speaker(
                    test_context, test_bgp_speaker),
                    payload['bgp_speaker'])
                create_bgp_sp.assert_called_once_with(test_context,
                                                      test_bgp_speaker)
                notify.assert_called_once_with(dr_resources.BGP_SPEAKER,
                                               events.AFTER_CREATE,
                                               self.plugin,
                                               payload=payload)
