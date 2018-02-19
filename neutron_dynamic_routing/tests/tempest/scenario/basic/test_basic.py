# Copyright (C) 2016 VA Linux Systems Japan K.K.
# Copyright (C) 2016 Fumihiko Kakuma <kakuma at valinux co jp>
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

from tempest import config
from tempest.lib import decorators

from neutron_dynamic_routing.tests.tempest.scenario import base as s_base
from neutron_dynamic_routing.tests.tempest.scenario.basic import base

from ryu.tests.integrated.common import docker_base as ctn_base

CONF = config.CONF


class BgpSpeakerBasicTest(base.BgpSpeakerBasicTestJSONBase):

    @decorators.idempotent_id('cc615252-c6cb-4d75-a70e-608fb2c3736a')
    def test_schedule_added_speaker(self):
        self.bgp_peer_args[0]['peer_ip'] = self.r_as_ip[0].split('/')[0]
        num, subnet = self.tnet_gen.next()
        mask = '/' + str(self.TPool.prefixlen)
        TNet = s_base.Net(name='', net=subnet, mask=self.TPool.prefixlen,
                          cidr=subnet + mask, router=None)
        TSubNet = s_base.SubNet(name='', cidr=TNet.cidr, mask=TNet.mask)
        MyRouter = s_base.Router(name='my-router' + str(num), gw='')
        ext_net_id = self.create_bgp_network(
            4, self.MyScope,
            self.PNet, self.PPool, self.PSubNet,
            self.TPool, [[TNet, TSubNet, MyRouter]])
        speaker_id, peers_ids = self.create_and_add_peers_to_speaker(
            ext_net_id,
            self.bgp_speaker_args,
            [self.bgp_peer_args[0]])
        self.check_remote_as_state(self.dr, self.r_ass[0],
                                   ctn_base.BGP_FSM_ESTABLISHED)

    @decorators.idempotent_id('ce98c33c-0ffa-49ae-b365-da836406793b')
    def test_unschedule_deleted_speaker(self):
        self.bgp_peer_args[0]['peer_ip'] = self.r_as_ip[0].split('/')[0]
        num, subnet = self.tnet_gen.next()
        mask = '/' + str(self.TPool.prefixlen)
        TNet = s_base.Net(name='', net=subnet, mask=self.TPool.prefixlen,
                          cidr=subnet + mask, router=None)
        TSubNet = s_base.SubNet(name='', cidr=TNet.cidr, mask=TNet.mask)
        MyRouter = s_base.Router(name='my-router' + str(num), gw='')
        ext_net_id = self.create_bgp_network(
            4, self.MyScope,
            self.PNet, self.PPool, self.PSubNet,
            self.TPool, [[TNet, TSubNet, MyRouter]])
        speaker_id, peers_ids = self.create_and_add_peers_to_speaker(
            ext_net_id,
            self.bgp_speaker_args,
            [self.bgp_peer_args[0]],
            auto_delete=False)
        self.check_remote_as_state(self.dr, self.r_ass[0],
                                   ctn_base.BGP_FSM_ESTABLISHED)
        self.delete_bgp_speaker(speaker_id)
        self.delete_bgp_peer(peers_ids[0])
        self.check_remote_as_state(self.dr, self.r_ass[0],
                                   ctn_base.BGP_FSM_ACTIVE,
                                   init_state=ctn_base.BGP_FSM_ESTABLISHED)

    @decorators.idempotent_id('aa6c565c-ded3-413b-8dc9-3928b3b0e38f')
    def test_remove_add_speaker_agent(self):
        self.bgp_peer_args[0]['peer_ip'] = self.r_as_ip[0].split('/')[0]
        num, subnet = self.tnet_gen.next()
        mask = '/' + str(self.TPool.prefixlen)
        TNet = s_base.Net(name='', net=subnet, mask=self.TPool.prefixlen,
                          cidr=subnet + mask, router=None)
        TSubNet = s_base.SubNet(name='', cidr=TNet.cidr, mask=TNet.mask)
        MyRouter = s_base.Router(name='my-router' + str(num), gw='')
        ext_net_id = self.create_bgp_network(
            4, self.MyScope,
            self.PNet, self.PPool, self.PSubNet,
            self.TPool, [[TNet, TSubNet, MyRouter]])
        speaker_id, peers_ids = self.create_and_add_peers_to_speaker(
            ext_net_id,
            self.bgp_speaker_args,
            [self.bgp_peer_args[0]])
        self.check_remote_as_state(self.dr, self.r_ass[0],
                                   ctn_base.BGP_FSM_ESTABLISHED)
        agent_list = self.bgp_client.list_dragents_for_bgp_speaker(
            speaker_id)['agents']
        self.assertEqual(1, len(agent_list))
        agent_id = agent_list[0]['id']
        self.bgp_client.remove_bgp_speaker_from_dragent(agent_id, speaker_id)
        self.check_remote_as_state(self.dr, self.r_ass[0],
                                   ctn_base.BGP_FSM_ACTIVE,
                                   init_state=ctn_base.BGP_FSM_ESTABLISHED)
        self.bgp_client.add_bgp_speaker_to_dragent(agent_id, speaker_id)
        self.check_remote_as_state(self.dr, self.r_ass[0],
                                   ctn_base.BGP_FSM_ESTABLISHED)
