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

from unittest import mock

import netaddr
from neutron.tests import base
from neutron_lib.callbacks import events
from neutron_lib.callbacks import registry
from neutron_lib.callbacks import resources
from neutron_lib import constants as n_const

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
        rpc_conn_p = mock.patch('neutron_lib.rpc.Connection')
        rpc_conn_p.start()
        admin_ctx_p = mock.patch('neutron_lib.context.get_admin_context')
        self.admin_ctx_m = admin_ctx_p.start()
        self.fake_admin_ctx = mock.Mock()
        self.admin_ctx_m.return_value = self.fake_admin_ctx
        self.plugin = bgp_plugin.BgpPlugin()

    def _create_test_payload(self, context='test_ctx'):
        bgp_speaker = {'id': '11111111-2222-3333-4444-555555555555'}
        payload = events.DBEventPayload(
                      context,
                      metadata={'plugin': self.plugin},
                      states=(bgp_speaker,))
        return payload

    def test__register_callbacks(self):
        with mock.patch.object(registry, 'subscribe') as subscribe:
            plugin = bgp_plugin.BgpPlugin()
            expected_calls = [
                mock.call(plugin.bgp_drscheduler.schedule_bgp_speaker_callback,
                          dr_resources.BGP_SPEAKER, events.AFTER_CREATE),
                mock.call(plugin.floatingip_update_callback,
                          resources.FLOATING_IP, events.AFTER_CREATE),
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
                mock.call(plugin.port_callback,
                          resources.PORT, events.AFTER_UPDATE),
            ]
            self.assertEqual(subscribe.call_args_list, expected_calls)

    def test_create_bgp_speaker(self):
        test_context = 'create_bgp_context'
        test_bgp_speaker = {'id': None}
        payload = self._create_test_payload(context=test_context)
        with mock.patch.object(bgp_db.BgpDbMixin,
                               'create_bgp_speaker') as create_bgp_sp:
            with mock.patch.object(registry, 'publish') as publish:
                create_bgp_sp.return_value = payload.latest_state
                self.assertEqual(self.plugin.create_bgp_speaker(
                    test_context, test_bgp_speaker),
                    payload.latest_state)
                create_bgp_sp.assert_called_once_with(test_context,
                                                      test_bgp_speaker)
                publish.assert_called_once_with(dr_resources.BGP_SPEAKER,
                                                events.AFTER_CREATE,
                                                self.plugin,
                                                payload=mock.ANY)
                publish_payload = publish.call_args_list[0][1]['payload']
                self.assertEqual(payload.latest_state,
                                 publish_payload.latest_state)
                self.assertEqual(payload.context, publish_payload.context)

    def test_floatingip_update_callback(self):
        new_fip = {'floating_ip_address': netaddr.IPAddress('10.10.10.10'),
                   'router_id': '', 'floating_network_id': 'a-b-c-d-e'}
        old_fip = new_fip.copy()
        old_fip.update(router_id='old-router-id')

        test_context = 'test_context'

        get_bpg_speakers_name = '_bgp_speakers_for_gw_network_by_family'
        with mock.patch.object(self.plugin, get_bpg_speakers_name) as get_bgp:
            with mock.patch.object(self.plugin,
                                   'stop_route_advertisements') as stop_ad:
                with mock.patch.object(self.plugin, '_bgp_rpc') as bgp_rpc:
                    bgp_speaker = mock.Mock()
                    bgp_speaker.id = '11111111-2222-3333-4444-555555555555'
                    get_bgp.return_value = [bgp_speaker]

                    self.plugin.floatingip_update_callback(
                        test_context, events.AFTER_UPDATE, None,
                        payload=events.DBEventPayload(
                            test_context, states=(old_fip, new_fip)))

                    get_bgp.assert_called_once_with(self.fake_admin_ctx,
                                                    'a-b-c-d-e',
                                                    n_const.IP_VERSION_4)

                    old_host_route = [{'destination': '10.10.10.10/32',
                        'next_hop': None}]
                    stop_ad.assert_called_once_with(self.fake_admin_ctx,
                                                    bgp_rpc,
                                                    bgp_speaker.id,
                                                    old_host_route)
